from src.agents.edges import decide_next_step
from src.agents.state import GraphState


def test_decide_next_step_routes_search() -> None:
    """
    Verifies that search_node is targeted when next_action is 'search'.
    """
    state: GraphState = {
        "messages": [],
        "search_query": "",
        "next_action": "search",
    }
    target = decide_next_step(state)
    assert target == "search_node"


def test_decide_next_step_routes_respond() -> None:
    """
    Verifies that generator_node is targeted when next_action is 'respond'.
    """
    state: GraphState = {
        "messages": [],
        "search_query": "",
        "next_action": "respond",
    }
    target = decide_next_step(state)
    assert target == "generator_node"
