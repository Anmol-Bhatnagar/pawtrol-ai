import logging
from typing import Any, Dict
from src.agents.state import GraphState
from src.agents.tools.search_tool import search_tool

logger = logging.getLogger(__name__)


def get_msg_role_and_content(msg: Any) -> tuple[str, str]:
    """
    Safely retrieves the role type and text content from either a dictionary
    or a LangChain BaseMessage class instance.
    """
    if hasattr(msg, "type"):
        # BaseMessage objects have msg.type: 'human', 'ai', 'tool', etc.
        role = msg.type
        content = getattr(msg, "content", "")
    elif isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = "user"
        content = str(msg)
    return role, content


def router_node(state: GraphState) -> Dict[str, Any]:
    """
    Evaluates the conversation context to determine if a search is needed.
    """
    logger.info("Routing user request...")
    messages = state.get("messages", [])

    if not messages:
        return {"search_query": "", "next_action": "respond"}

    # Fetch last message text
    last_message = messages[-1]
    _, content = get_msg_role_and_content(last_message)
    content_lower = content.lower()

    # Rule-based router for boilerplate execution (can be replaced with LLM parsing JSON)
    if any(keyword in content_lower for keyword in ["search", "find", "query", "lookup"]):
        # Extract query text
        logger.info(f"Router decided: USE TOOL (Query: '{content}')")
        return {"search_query": content, "next_action": "search"}

    logger.info("Router decided: RESPOND DIRECTLY")
    return {"search_query": "", "next_action": "respond"}


def search_node(state: GraphState) -> Dict[str, Any]:
    """
    Invokes the search tool and logs the output in the message flow.
    """
    logger.info("Invoking Search Node...")
    query = state.get("search_query", "FastAPI LangGraph boilerplate")

    # Execute search tool
    tool_output = search_tool.invoke(query)

    # Return message update to be appended
    return {
        "messages": [
            {
                "role": "tool",
                "content": tool_output,
                "name": "search_tool",
                "tool_call_id": "mock_search_tool_call_id",
            }
        ]
    }


def generator_node(state: GraphState) -> Dict[str, Any]:
    """
    Generates the final response for the user.
    """
    logger.info("Invoking Generator Node...")
    messages = state.get("messages", [])

    if not messages:
        return {
            "messages": [
                {
                    "role": "assistant",
                    "content": "Hello! I am ready. How can I help you?",
                }
            ]
        }

    last_msg = messages[-1]
    role, content = get_msg_role_and_content(last_msg)

    # Generate reply based on last message type
    if role == "tool":
        reply = (
            f"Here is what I found from search tool: {content}"
        )
    else:
        reply = (
            f"I received your request: '{content}'. "
            f"Please let me know if you would like me to 'search' for anything specific!"
        )

    return {"messages": [{"role": "assistant", "content": reply}]}
