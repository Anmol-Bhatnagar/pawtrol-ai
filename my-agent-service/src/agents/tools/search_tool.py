import logging
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_tool(query: str) -> str:
    """
    Searches the internet or internal databases for information related to the query.
    Use this tool whenever the user asks for real-time information or specific documentation facts.
    """
    logger.info(f"search_tool tool invoked with query: '{query}'")

    # In production, integrate Tavily, Serper, Google Search, or an internal retriever.
    # Returns mock search results matching the query structure.
    return (
        f"Search Results for '{query}': Found documents verifying that the service "
        f"is successfully configured and that FastAPI router endpoints are functional."
    )
