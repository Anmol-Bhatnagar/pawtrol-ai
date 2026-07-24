import os
import shutil
import tempfile
from unittest.mock import MagicMock, patch
from langchain_core.runnables import RunnableConfig
from src.agents.nodes import agent_node
from src.agents.state import GraphState
from src.agents.tools.classify_tool import classify_dog_image_tool


def test_classify_dog_image_tool_caching_and_memory():
    """
    Validates that classify_dog_image_tool caches ONNX outputs locally,
    returns predictions from cache on subsequent hits, and updates
    agent system prompts with local memory context.
    """
    # 1. Create a temporary folder for images and mocks
    temp_dir = tempfile.mkdtemp()
    test_image_path = os.path.join(temp_dir, "test_dog.jpg")

    # Write a dummy image file
    from PIL import Image

    img = Image.new("RGB", (100, 100), color=(0, 255, 0))
    img.save(test_image_path)

    # Define paths inside temp_dir to avoid writing to real production directories
    temp_cache_dir = os.path.join(temp_dir, "predictions")
    temp_session_dir = os.path.join(temp_dir, "sessions")

    mock_predictions = [{"breed": "pug", "confidence": 0.95}]

    # 2. Patch the directories and model predict method
    with (
        patch("src.agents.tools.classify_tool.CACHE_DIR", temp_cache_dir),
        patch("src.agents.tools.classify_tool.SESSION_DIR", temp_session_dir),
        patch("src.agents.nodes.SESSION_DIR", temp_session_dir),
        patch(
            "src.services.dog_classifier.dog_classifier.predict",
            return_value=mock_predictions,
        ) as mock_predict,
    ):
        # Configuration
        config: RunnableConfig = {
            "configurable": {"thread_id": "test-thread-123"}
        }

        # --- First Execution: Cache Miss ---
        result = classify_dog_image_tool.invoke(
            {"image_path": test_image_path}, config=config
        )

        # Verify prediction model was called
        mock_predict.assert_called_once()
        assert "Executed classification model" in result
        assert "pug (95.00%)" in result

        # Verify cache and session files were created
        assert len(os.listdir(temp_cache_dir)) == 1
        assert len(os.listdir(temp_session_dir)) == 1

        # --- Second Execution: Cache Hit ---
        mock_predict.reset_mock()
        result_cached = classify_dog_image_tool.invoke(
            {"image_path": test_image_path}, config=config
        )

        # Verify prediction model was NOT called this time (loaded from cache)
        mock_predict.assert_not_called()
        assert "Loaded from local cache" in result_cached
        assert "pug (95.00%)" in result_cached

        # --- Test Agent Prompt Memory Injection ---
        state: GraphState = {
            "messages": [
                {"role": "user", "content": "How heavy does my dog get?"}
            ],
            "search_query": "",
            "next_action": "",
        }

        # Patch get_llm to return a mock LLM that we can verify
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm

        with patch("src.agents.nodes.get_llm", return_value=mock_llm):
            agent_node(state, config=config)

            # Verify mock_llm was invoked
            mock_llm.invoke.assert_called_once()

            # Get the messages passed to the mock LLM
            called_messages = mock_llm.invoke.call_args[0][0]
            system_msg = called_messages[0]

            # Verify system message has the cached classification results
            assert "Memory Context" in system_msg.content
            assert "test_dog.jpg" in system_msg.content
            assert "pug (95.00%)" in system_msg.content

    # Cleanup
    shutil.rmtree(temp_dir)
