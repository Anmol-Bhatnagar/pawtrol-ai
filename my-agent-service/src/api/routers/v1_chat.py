import json
import logging
from typing import AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from src.agents.graph import graph
from src.api.dependencies.auth import verify_api_key
from src.api.schemas.chat import ChatRequest, ChatResponse, Message

router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


@router.post(
    "/completions",
    response_model=ChatResponse,
    dependencies=[Depends(verify_api_key)],
)
async def chat_completion(request: ChatRequest) -> ChatResponse | StreamingResponse:
    """
    Executes the LLM/LangGraph agent network. Supports synchronous responses
    and standard event streams (SSE).
    """
    # Map input messages to the state payload.
    # We will build LangChain messages (HumanMessage, AIMessage, etc.) inside graph nodes
    # or handle list-of-dict structures.
    initial_state = {
        "messages": [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
    }

    # Configuration extraction
    config = request.config or {}
    thread_id = config.get("thread_id", "default-thread")
    run_config = {"configurable": {"thread_id": thread_id}}

    if request.stream:

        async def stream_generator() -> AsyncGenerator[str, None]:
            try:
                # Stream the event transitions from the graph
                async for chunk in graph.astream(initial_state, run_config):
                    # chunk is a dictionary of node state output (e.g., {'node_name': state})
                    yield f"data: {json.dumps(chunk)}\n\n"
            except Exception as e:
                logger.error(
                    f"Agent workflow stream failed: {e}", exc_info=True
                )
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

        return StreamingResponse(
            stream_generator(), media_type="text/event-stream"
        )

    try:
        # Run graph workflow through to completion
        final_state = await graph.ainvoke(initial_state, run_config)
        messages = final_state.get("messages", [])

        if not messages:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="The agent execution succeeded but returned an empty response state.",
            )

        # Retrieve the final message in the sequence
        last_msg = messages[-1]

        # Extract role and content from standard dictionary representation
        if isinstance(last_msg, dict):
            role = last_msg.get("role", "assistant")
            content = last_msg.get("content", "")
        else:
            # Handle if nodes write LangChain message structures directly
            role = "assistant"
            content = getattr(last_msg, "content", str(last_msg))

        return ChatResponse(
            message=Message(role=role, content=content),
            metadata={"messages_count": len(messages)},
        )

    except Exception as e:
        logger.error(f"Agent workflow execution failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent workflow execution failed: {str(e)}",
        )
