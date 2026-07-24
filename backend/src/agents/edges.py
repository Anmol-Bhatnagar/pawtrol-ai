import logging
from src.agents.state import GraphState

logger = logging.getLogger(__name__)


def decide_next_step(state: GraphState) -> str:
    """
    Conditional routing edge function.
    Handles both legacy state actions and standard ReAct tool calling routes.
    """
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        tool_calls = getattr(last_msg, "tool_calls", [])
        if not tool_calls and isinstance(last_msg, dict):
            tool_calls = last_msg.get("tool_calls", [])

        if tool_calls:
            logger.info("decide_next_step decided: route to tools_node.")
            return "tools_node"

    next_action = state.get("next_action")
    logger.info(f"Evaluating conditional edge: action => {next_action}")

    if next_action == "search":
        return "search_node"
    elif next_action == "respond":
        return "generator_node"

    return "end"
