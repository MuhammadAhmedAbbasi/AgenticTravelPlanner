# Libraries

from langchain.agents import create_agent

from src.prompts.final_trip_planner_prompts import main_agent_system_prompt
from src.tools.distance_measurement_tool import distance_measurement_tool
from src.tools.web_search_tool import web_search_tool
# from src.middlewares.final_trip_planner_middlewares import switch_system_prompt

class FinalTripPlanner:
    def __init__(self, model, tools, prompt):
        self.agent = self.agent_intialize(model, tools, prompt)

    def agent_intialize(self, model, tools, prompt):
        # 5. Create the Agent Graph
        return create_agent(
            model=model, 
            tools=tools, 
            system_prompt=prompt,
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