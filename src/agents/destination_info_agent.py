# Libraries
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools.attraction_finding_tool import attraction_finding_tool
from src.tools.hotel_tool import hotel_finding_tool
from src.tools.restaurant_tool import restaurant_finding_tool

model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, max_retries = 3, timeout=90)
checkpointer = InMemorySaver()
tools = [attraction_finding_tool, hotel_finding_tool, restaurant_finding_tool]

class DestinationInfoAgent:
    def __init__(self, model, tools):

        prompt = self.prompt_initialize()
        self.agent = self.agent_intialize(model, tools, prompt)

    def prompt_initialize(self) -> str:
        # 4. Define System Prompt
        return """You are CityDiscoveryAdvisor. Find attractions, hotels, and restaurants for cities using TripAdvisor tools.

                    TOOLS:
                    - attraction_finding_tool(place_name): Top 5 attractions
                    - hotel_finding_tool(place_name): Top 5 hotels
                    - restaurant_finding_tool(place_name): Top 5 restaurants

                    USAGE:
                    - "things to do" → attractions
                    - "where to stay" → hotels
                    - "where to eat" → restaurants
                    - General city query → use all 3 tools

                    RULES:
                    1. Only use tool outputs, never fabricate data
                    2. If tool returns error, report: "No {category} found for {place}"
                    3. Present all results (up to 5 per category)

                    FORMAT:
                    **{Category} in {City}:**
                    1. {Name} ({Rating}) - {Description}
                    "{Highlighted Review}"

                    **Note:** {Any errors or limitations}

                    Crticial Rules:
                        - If the results are not found for any specific place then instead of throwing error, check the place if it is correct and if it is not correct, correct and again try.
                        - The name of place can be either country, city or province so if anyone give wrong name, correct it and then use.
                        - If there are more than one city or countries then you have to find details for all of the given cities and detail. use tools to find detail of each place and then finally give the result including all the asked places.
            """
    def agent_intialize(self, model, tools, prompt):
        # 5. Create the Agent Graph
        return create_agent(
            model=model, 
            tools=tools, 
            system_prompt=prompt
            )

    def invoke(self, user_input: str):
        """
        Run the agent with a user query.
        Args:
            user_input (str): The user's prompt (e.g., "Flights from LHE to JFK").
            thread_id (str): Unique ID for conversation memory.
        """
        res = self.agent.invoke(user_input)
        
        # Return the last message (the AI's response)
        return res