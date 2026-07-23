from src.agents.nodes import generator_node, router_node, search_node
from src.agents.state import GraphState


def test_router_node_direct() -> None:
    """
    Ensures standard messages are routed to direct responses.
    """
    state: GraphState = {
        "messages": [{"role": "user", "content": "Greetings agent!"}],
        "search_query": "",
        "next_action": "",
    }
    updates = router_node(state)
    assert updates["next_action"] == "respond"
    assert updates["search_query"] == ""


def test_router_node_search() -> None:
    """
    Ensures search-intent trigger terms redirect execution to tools.
    """
    state: GraphState = {
        "messages": [{"role": "user", "content": "Please query weather info"}],
        "search_query": "",
        "next_action": "",
    }
    updates = router_node(state)
    assert updates["next_action"] == "search"
    assert updates["search_query"] == "Please query weather info"


def test_search_node_updates() -> None:
    """
    Verifies the search node returns tool reply blocks matching query parameters.
    """
    state: GraphState = {
        "messages": [],
        "search_query": "mock search terms",
        "next_action": "search",
    }
    updates = search_node(state)
    assert "messages" in updates
    assert len(updates["messages"]) == 1
    assert updates["messages"][0]["role"] == "tool"
    assert "mock search terms" in updates["messages"][0]["content"]


def test_generator_node_updates() -> None:
    """
    Ensures generator nodes build assistant output contexts correctly.
    """
    state: GraphState = {
        "messages": [{"role": "user", "content": "hello"}],
        "search_query": "",
        "next_action": "respond",
    }
    updates = generator_node(state)
    assert "messages" in updates
    assert len(updates["messages"]) == 1
    assert updates["messages"][0]["role"] == "assistant"
