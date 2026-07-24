import logging
from typing import Any, List, Optional
from langchain_core.language_models.chat_models import SimpleChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.callbacks import CallbackManagerForLLMRun
from src.config.settings import settings

logger = logging.getLogger(__name__)


class MockChatModel(SimpleChatModel):
    """
    Mock LLM to run conversation flows and tool triggering in offline,
    testing, or fallback environments.
    """

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # SimpleChatModel requires implementing _call. We delegate to _generate.
        raise NotImplementedError("SimpleChatModel _call should not be reached when _generate is overridden.")

    @property
    def _llm_type(self) -> str:
        return "mock-chat-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Retrieve final message content
        last_message = messages[-1].content
        last_message_lower = last_message.lower()

        # Check if user is triggering search (to support existing tests)
        if any(
            kw in last_message_lower
            for kw in ["search", "find", "query", "lookup"]
        ):
            message = AIMessage(
                content=(
                    f"Here is what I found from search tool: Search Results for '{last_message}': "
                    "Found documents verifying that the service is successfully configured and "
                    "that FastAPI router endpoints are functional."
                )
            )
        # Check if user is triggering dog breed classification
        elif any(
            kw in last_message_lower
            for kw in ["classify", "predict", "image", "breed", "dog"]
        ):
            # Parse path if provided, e.g. 'c:\dog.jpg' or '/tmp/dog.png'
            import re

            path_match = re.search(
                r"([a-zA-Z]:\\[^\s]+|\/[^\s]+|\S+\.(?:jpg|jpeg|png|webp|svg))",
                last_message,
            )
            path = path_match.group(0) if path_match else "dummy_dog.jpg"

            tool_call = {
                "name": "classify_dog_image_tool",
                "args": {"image_path": path},
                "id": "call_mock_id_123",
            }
            message = AIMessage(
                content="",
                additional_kwargs={"tool_calls": [tool_call]},
                tool_calls=[tool_call],
            )
        else:
            # Direct response (supports existing direct chat tests)
            message = AIMessage(
                content=(
                    f"I received your request: '{last_message}'. "
                    "Please let me know if you would like me to 'search' for anything specific!"
                )
            )

        return ChatResult(generations=[ChatGeneration(message=message)])

    def bind_tools(self, tools: List[Any], **kwargs: Any) -> "MockChatModel":
        return self


def get_llm() -> Any:
    """
    Returns the appropriate LLM client based on environment configurations,
    falling back to a conversational MockChatModel if no keys are found.
    """
    is_testing = settings.ENVIRONMENT == "testing"

    openai_key = settings.OPENAI_API_KEY
    if openai_key and not is_testing and not openai_key.startswith("sk-...") and "mock" not in openai_key.lower():
        try:
            from langchain_openai import ChatOpenAI

            logger.info("Initializing OpenAI Chat Model...")
            return ChatOpenAI(
                model=settings.OPENAI_MODEL_NAME,
                openai_api_key=openai_key,
                temperature=0.0,
            )
        except ImportError:
            logger.warning(
                "langchain-openai not installed despite OPENAI_API_KEY. Falling back..."
            )

    anthropic_key = settings.ANTHROPIC_API_KEY
    if anthropic_key and not is_testing and not anthropic_key.startswith("sk-ant-...") and "mock" not in anthropic_key.lower():
        try:
            from langchain_anthropic import ChatAnthropic

            logger.info("Initializing Anthropic Chat Model...")
            return ChatAnthropic(
                model=settings.ANTHROPIC_MODEL_NAME,
                anthropic_api_key=anthropic_key,
                temperature=0.0,
            )
        except ImportError:
            logger.warning(
                "langchain-anthropic not installed despite ANTHROPIC_API_KEY. Falling back..."
            )

    logger.info(
        "No LLM provider keys set or libraries missing. Initializing MockChatModel fallback."
    )
    return MockChatModel()
