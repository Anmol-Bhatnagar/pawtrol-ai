import logging
from src.agents.state import GraphState

logger = logging.getLogger(__name__)


def decide_next_step(state: GraphState) -> str:
    """
    Conditional routing edge function. Matches the `next_action` key
    to redirect graph traversal to search_node or generator_node.
    """
    next_action = state.get("next_action", "respond")
    logger.info(f"Evaluating conditional edge: action => {next_action}")

    if next_action == "search":
        return "search_node"

    return "generator_node"
