import json
import logging
import os
from typing import Any, Dict, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from src.agents.llm import get_llm
from src.agents.state import GraphState
from src.agents.tools.classify_tool import classify_dog_image_tool, SESSION_DIR
from src.agents.tools.search_tool import search_tool

logger = logging.getLogger(__name__)

# List of tools available
tools_map = {
    "classify_dog_image_tool": classify_dog_image_tool,
    "search_tool": search_tool,
}


def get_msg_role_and_content(msg: Any) -> tuple[str, str]:
    """
    Safely retrieves the role type and text content from either a dictionary
    or a LangChain BaseMessage class instance.
    """
    if hasattr(msg, "type"):
        role = msg.type
        content = getattr(msg, "content", "")
    elif isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = "user"
        content = str(msg)
    return role, content


# --- Backward Compatibility Nodes for existing tests ---


def router_node(state: GraphState) -> Dict[str, Any]:
    """
    Evaluates the conversation context to determine if a search is needed.
    """
    logger.info("Routing user request...")
    messages = state.get("messages", [])

    if not messages:
        return {"search_query": "", "next_action": "respond"}

    last_message = messages[-1]
    _, content = get_msg_role_and_content(last_message)
    content_lower = content.lower()

    if any(
        keyword in content_lower
        for keyword in ["search", "find", "query", "lookup"]
    ):
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
    tool_output = search_tool.invoke(query)
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

    if role == "tool":
        reply = f"Here is what I found from search tool: {content}"
    else:
        reply = (
            f"I received your request: '{content}'. "
            f"Please let me know if you would like me to 'search' for anything specific!"
        )

    return {"messages": [{"role": "assistant", "content": reply}]}


# --- New ReAct Agent Nodes with Local Memory Context ---


def agent_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Agent node representing the core reasoning step. Prepares the system prompt,
    injects any locally stored dog classification results as memory context, and invokes
    the selected LLM with custom tools bound.
    """
    logger.info("Invoking Agent Node...")

    # 1. Retrieve the thread_id
    thread_id = (
        config.get("configurable", {}).get("thread_id", "default-thread")
    )

    # 2. Check if a local session prediction memory exists
    classification_context = ""
    session_file = os.path.join(SESSION_DIR, f"{thread_id}.json")
    if os.path.exists(session_file):
        try:
            with open(session_file, "r") as f:
                session_data = json.load(f)
            predictions = session_data.get("predictions", [])
            image_path = session_data.get("image_path", "")
            if predictions:
                pred_strings = [
                    f"{p['breed']} ({p['confidence']:.2%})" for p in predictions
                ]
                classification_context = (
                    f"\n[Memory Context: The user previously uploaded and classified a dog image from path '{image_path}'. "
                    f"The classification results were: {', '.join(pred_strings)}. Use this information to converse about "
                    "the dog, its traits, care, training, or health if the user refers to it (e.g. 'my dog', 'this dog', "
                    "or 'the image').]\n"
                )
                logger.info(
                    f"Loaded locally stored classification memory for thread '{thread_id}'."
                )
        except Exception as e:
            logger.warning(f"Failed to read session cache file: {e}")

    # 3. Build system instruction prompt
    system_prompt = (
        "You are an expert AI dog assistant. You help users identify dog breeds and answer questions about "
        "dog care, training, health, behavior, and traits. You have access to a dog breed classification tool "
        "('classify_dog_image_tool') which runs a deep learning MobileNetV3 model on local image paths, and a "
        "general search tool ('search_tool') for checking facts."
    )
    if classification_context:
        system_prompt += classification_context

    # 4. Format messages from GraphState to LangChain message instances
    raw_messages = state.get("messages", [])
    formatted_messages = [SystemMessage(content=system_prompt)]

    for msg in raw_messages:
        if isinstance(msg, dict):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            name = msg.get("name")
            tool_call_id = msg.get("tool_call_id")

            # Map standard roles
            if role == "system":
                formatted_messages.append(SystemMessage(content=content))
            elif role == "user":
                formatted_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                additional_kwargs = msg.get("additional_kwargs", {})
                tool_calls = msg.get("tool_calls", [])
                formatted_messages.append(
                    AIMessage(
                        content=content,
                        additional_kwargs=additional_kwargs,
                        tool_calls=tool_calls,
                    )
                )
            elif role == "tool":
                formatted_messages.append(
                    ToolMessage(
                        content=content, name=name, tool_call_id=tool_call_id
                    )
                )
        else:
            formatted_messages.append(msg)

    # 5. Get the LLM client and bind tools
    llm = get_llm()
    llm_with_tools = llm.bind_tools(list(tools_map.values()))

    # 6. Execute LLM invocation
    response = llm_with_tools.invoke(formatted_messages)

    # Return output message to be appended to the state
    return {"messages": [response]}


def tools_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Executes any tools requested in the last message's tool calls and appends
    the ToolMessage results back to the message history.
    """
    logger.info("Invoking Tools Node...")
    messages = state.get("messages", [])
    if not messages:
        return {"messages": []}

    last_msg = messages[-1]
    tool_outputs = []

    # Extract tool calls from the AIMessage
    tool_calls = getattr(last_msg, "tool_calls", [])
    if not tool_calls and isinstance(last_msg, dict):
        tool_calls = last_msg.get("tool_calls", [])

    for tool_call in tool_calls:
        tool_name = tool_call.get("name")
        tool_args = tool_call.get("args", {})
        tool_id = tool_call.get("id")

        logger.info(
            f"Executing tool '{tool_name}' with args {tool_args}..."
        )

        if tool_name in tools_map:
            selected_tool = tools_map[tool_name]
            try:
                # Call tool with Config to pass context down
                output = selected_tool.invoke(tool_args, config=config)
            except Exception as e:
                output = f"Error: Tool execution failed. {str(e)}"
        else:
            output = f"Error: Tool '{tool_name}' not found."

        tool_outputs.append(
            ToolMessage(
                content=str(output), name=tool_name, tool_call_id=tool_id
            )
        )

    return {"messages": tool_outputs}
