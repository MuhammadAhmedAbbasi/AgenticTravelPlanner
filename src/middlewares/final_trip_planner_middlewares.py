from langchain.agents.middleware import before_model, ModelRequest
from typing import Any
from src.prompts.final_trip_planner_prompts import prompts
from langchain.messages import SystemMessage


@before_model
def switch_system_prompt(state: Any, runtime: Any) -> dict[str, Any] | None:
    """
    Switch the prompt based on the usecase
    """
    # Example condition: check a key in agent state
    if state.get("task_mode") == "Travel_Plan":
        new_prompt = prompts["main_agent_system_prompt"]
    else:
        new_prompt = prompts["update_agent_system_prompt"]
    
    # Use a SystemMessage to override the prompt for this model request
    return {"system_message": SystemMessage(content=new_prompt)}