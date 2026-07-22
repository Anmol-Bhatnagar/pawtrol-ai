from src.agents.tools.search_tool import search_tool


def test_search_tool_execution() -> None:
    """
    Verifies that the search tool returns a response containing the original query.
    """
    result = search_tool.invoke("my test search query")
    assert "my test search query" in result
    assert "Search Results for" in result
