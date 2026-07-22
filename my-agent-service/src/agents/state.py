from typing import Annotated, Any, Dict, List, TypedDict
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    """
    Represents the operational state of the graph.
    """

    # Accumulates messages throughout execution via standard LangGraph list append utility
    messages: Annotated[List[Dict[str, Any]], add_messages]

    # Tracks intermediate extraction keys
    search_query: str

    # Directs routing instructions
    next_action: str
