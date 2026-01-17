import os
from typing import Literal, List, Optional
from datetime import datetime

# LangChain / LangGraph Imports
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from src.agents.destination_info_agent import DestinationInfoAgent
from src.agents.final_trip_planner_agent import FinalTripPlanner
from src.agents.info_gather_agent import InformationGatherChatbot
from src.agents.flight_search_agent import FlightSpecialistAgent

from src.tools.attraction_finding_tool import attraction_finding_tool
from src.tools.hotel_tool import hotel_finding_tool
from src.tools.restaurant_tool import restaurant_finding_tool
from src.tools.flight_search_tool import One_way_flight_search
from src.tools.web_search_tool import web_search_tool
from src.tools.distance_measurement_tool import distance_measurement_tool
from src.tools.time_gather_tool import time_tool

from src.utils.helping_class.conversation_format import ConversationFormat
from src.utils.http.custom_states import CustomState

from src.prompts.final_trip_planner_prompts import main_agent_system_prompt
from src.config.settings import settings

os.environ["GOOGLE_API_KEY"] = settings.google_api_key

class TravelAutomationSystem:
    def __init__(self):
        """
        Initialize the system ONCE.
        This sets up the shared model, tools, and the graph definition.
        """
        # 1. Shared Resources
        self.checkpointer = InMemorySaver() 
        self.model = ChatGoogleGenerativeAI(model=settings.flash_model, temperature=0, api_key = settings.google_api_key)
        self.mainmodel = ChatGoogleGenerativeAI(model=settings.pro_model, temperature=0, api_key = settings.google_api_key)
        
        # 2. Initialize Sub-Agents (Shared Instances)
        self.info_gather_agent = InformationGatherChatbot(self.model, ConversationFormat, [time_tool])
        self.flight_agent = FlightSpecialistAgent(self.model, [One_way_flight_search])
        self.trip_advisor_agent = DestinationInfoAgent(self.model, [attraction_finding_tool, hotel_finding_tool, restaurant_finding_tool])
        self.travel_partner = FinalTripPlanner(self.mainmodel, [web_search_tool, distance_measurement_tool], main_agent_system_prompt)

        # 3. Build the Graph
        self.app = self._build_workflow()

    def _build_workflow(self):
        """
        Constructs the LangGraph workflow.
        """
        workflow = StateGraph(CustomState)
        
        # Register Nodes
        workflow.add_node("gather_info_node", self.gather_info_node)
        workflow.add_node("search_flights", self.flight_node)
        workflow.add_node("search_hotels", self.accommodation_node)
        workflow.add_node("compile_itinerary", self.itinerary_compiler_node)

        # Register Edges & Conditions
        workflow.add_conditional_edges(
            START, 
            self.node_switch_condition, 
            {"gather_info_node": "gather_info_node", "travel_partner_node": "compile_itinerary"}
        )
        
        workflow.add_conditional_edges(
            "gather_info_node", 
            self.conditional_move, 
            ["search_flights", "search_hotels", END]
        )
        
        workflow.add_edge("search_flights", "compile_itinerary")
        workflow.add_edge("search_hotels", "compile_itinerary")
        workflow.add_edge("compile_itinerary", END)
        
        # Compile with the shared checkpointer
        return workflow.compile(checkpointer=self.checkpointer)

    # --- HELPER FOR UPDATES ---
    def _send_update(self, config: RunnableConfig, message: str):
        """Helper to send status updates if a callback exists in config."""
        if config and "configurable" in config:
            on_update = config["configurable"].get("on_update")
            if on_update:
                on_update(message)

    # --- NODE IMPLEMENTATIONS ---

    def gather_info_node(self, state: CustomState, config: RunnableConfig):
        self._send_update(config, "🤖 Analyzing your request...")
        print("--- Gathering Info Node ---")
        
        # 1. Get User Input
        messages = state.get("messages", [])
        if not messages:
            return {"messages": [AIMessage(content="Error: No messages found.")]}
        
        last_message = messages[-1]
        user_input = last_message.content if hasattr(last_message, 'content') else last_message['content']

        # 2. Identify what is CURRENTLY missing
        required_fields = ["Departure", "Destination", "StartDate", "Duration", "Budget", "Interest", "ExtraDetail"]
        current_missing = []
        
        for field in required_fields:
            val = state.get(field)
            if val is None or val in ["None", "Null", "null"] or (isinstance(val, list) and (len(val) == 0 or val == ['None'])):
                current_missing.append(field)
                
        # 3. Call Chatbot
        extracted_data = self.info_gather_agent.ask(user_input, missing_list=current_missing)
        
        # 4. MERGE LOGIC
        final_updates = {}
        for field in required_fields:
            new_val = extracted_data.get(field)
            old_val = state.get(field)
            
            is_new_empty = False
            if new_val is None:
                is_new_empty = True
            elif isinstance(new_val, str) and new_val.lower() in ["none", "null", ""]:
                is_new_empty = True
            elif isinstance(new_val, list):
                if len(new_val) == 0:
                    is_new_empty = True
                elif all(str(x).lower() in ["none", "null"] for x in new_val):
                    is_new_empty = True
            
            if not is_new_empty:
                final_updates[field] = new_val
            else:
                final_updates[field] = old_val
                
        # 5. Re-Check Completion
        is_complete = True
        for field in required_fields:
            val = final_updates.get(field)
            
            is_val_empty = False
            if val is None:
                is_val_empty = True
            elif isinstance(val, str) and val.lower() in ["none", "null", ""]:
                is_val_empty = True
            elif isinstance(val, list):
                if len(val) == 0 or all(str(x).lower() in ["none", "null"] for x in val):
                    is_val_empty = True
            
            if is_val_empty:
                is_complete = False
                break

        return {
            "Departure": final_updates["Departure"],
            "Destination": final_updates["Destination"],
            "StartDate": final_updates["StartDate"],
            "Duration": final_updates["Duration"],
            "Budget": final_updates["Budget"],
            "Interest": final_updates["Interest"],
            "ExtraDetail": final_updates["ExtraDetail"],
            "AllDetails": is_complete,
            "messages": [AIMessage(content=extracted_data["Response"])]
        }

    def flight_node(self, state: CustomState, config: RunnableConfig):
        self._send_update(config, "✈️  Searching for the best flights...")
        if not state.get('Departure') or not state.get('Destination'):
            return {"flight_info": "Flight details skipped due to missing info."}
        
        dest = state['Destination'][0] if isinstance(state['Destination'], list) else state['Destination']
        prompt = f"Find one-way flights from {state['Departure']} to {dest} on {state['StartDate']}. Provide a summary."
        
        print(f"--- Flight Node (Running) for {dest} ---")
        result = self.flight_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        flight_content = result.get("messages")[-1].content[0].get('text')
        print("Flight Info Captured.") 
        return {"flight_info": flight_content}

    def accommodation_node(self, state: CustomState, config: RunnableConfig):
        self._send_update(config, "🏨  Searching for hotels and attractions...")
        print("--- Hotel, Restaurant and Attraction Node (Running) ---")
        prompt = f"I'm going to {state.get('Destination')} for {state.get('Duration')} days."
        result = self.trip_advisor_agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        hotel_content = result.get("messages")[-1].content[0].get('text')
        print(f"Hotel Content: {result}")
        print("Accommodation Info Captured.")
        return {"hotel_info": hotel_content}

    def itinerary_compiler_node(self, state: CustomState, config: RunnableConfig):
        print(f"""

        DATA SOURCE 1 (Flights): {state.get('flight_info')}
        DATA SOURCE 2 (Hotels): {state.get('hotel_info')}

        """)
        self._send_update(config, "📝  Compiling your final itinerary...")
        # 1. Prepare Prompt based on mode
        if state.get("TravelMode") == "Travel_Plan":
            prompt = f"""
            I want to go to {state['Destination']} from {state['Departure']} for {state['Duration']}. 
            Start: {state['StartDate']}. Interests: {state['Interest']}. Budget: {state['Budget']} 
            Extra: {state['ExtraDetail']}
            
            DATA SOURCE 1 (Flights): {state.get('flight_info')}
            DATA SOURCE 2 (Hotels): {state.get('hotel_info')}
            
            Task: Combine this into a final formatted itinerary report.
            """
        else:
            # Revision Logic
            last_message = state['messages'][-1]
            user_input = last_message.content if hasattr(last_message, 'content') else last_message['content']
            prompt = f"""
            Fix the plan based on this concern: {user_input}
            Previous Plan: {state.get("previous_plan")}
            """

        print("--- Streaming Final Itinerary ---")
        
        input_payload = {
            "messages": [{"role": "user", "content": prompt}],
            "task_mode": state.get("TravelMode", "Travel_Plan")
        }
        
        result = self.travel_partner.invoke(input_payload)
        
        if isinstance(result, dict) and 'messages' in result:
             full_response = result['messages'][-1].content
             if isinstance(full_response, list): 
                 full_response = full_response[0]['text']
        else:
            full_response = str(result)

        return {
            "messages": [AIMessage(content=full_response)], 
            "previous_plan": full_response
        }

    # --- CONDITIONAL LOGIC ---

    def conditional_move(self, state: CustomState, config: RunnableConfig):
        if state.get("AllDetails") is True:
            self._send_update(config, "All_Details_Fetched")
            return ["search_flights", "search_hotels"]
        return END

    def node_switch_condition(self, state: CustomState):
        if state.get("move_to_info_chatbot") is True or state.get("TravelMode") == "Revision_Plan":
             return "travel_partner_node"
        return "gather_info_node"

    # --- PUBLIC API ---

    def run_trip_planner(self, user_id: str, user_input: str, mode: str = "Travel_Plan", on_update=None):
        """
        The main entry point for your API or UI.
        Accepts an optional on_update callback.
        """
        # Inject the callback into 'configurable'
        config = {
            "configurable": {
                "thread_id": user_id,
                "on_update": on_update
            }
        }
        
        initial_state = {
            "messages": [{"role": "user", "content": user_input}],
            "TravelMode": mode
        }
        
        # Run the graph
        final_state = self.app.invoke(initial_state, config=config)
        
        # Return the last message
        return final_state['messages'][-1].content

trip_system = TravelAutomationSystem()