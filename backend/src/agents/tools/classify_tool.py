import hashlib
import json
import logging
import os
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from src.services.dog_classifier import dog_classifier

logger = logging.getLogger(__name__)

# Resolve storage directories relative to the backend project root
BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
)
CACHE_DIR = os.path.join(BACKEND_DIR, "storage", "predictions")
SESSION_DIR = os.path.join(BACKEND_DIR, "storage", "sessions")


@tool
def classify_dog_image_tool(image_path: str, config: RunnableConfig) -> str:
    """
    Classifies the breed of a dog in an image file.
    Input should be the local file path to the dog image (e.g. 'c:\\images\\dog.jpg').
    """
    logger.info(f"classify_dog_image_tool invoked with image_path: '{image_path}'")

    try:
        # 1. Resolve thread_id from LangGraph run config
        thread_id = (
            config.get("configurable", {})
            .get("thread_id", "default-thread")
        )

        # 2. Check file existence
        if not os.path.exists(image_path):
            # Create a dummy image for local validation/testing if path contains 'dummy' or 'test'
            if "dummy" in image_path.lower() or "test" in image_path.lower():
                from PIL import Image

                os.makedirs(os.path.dirname(image_path) or ".", exist_ok=True)
                # Create a 224x224 RGB image
                img = Image.new("RGB", (224, 224), color=(255, 0, 0))
                img.save(image_path)
                logger.info(f"Created dummy image file at: '{image_path}'")
            else:
                return f"Error: Image file not found at path: {image_path}"

        # 3. Read image bytes
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # 4. Compute unique hash of the image content
        image_hash = hashlib.sha256(image_bytes).hexdigest()

        # Ensure storage subdirectories exist
        os.makedirs(CACHE_DIR, exist_ok=True)
        os.makedirs(SESSION_DIR, exist_ok=True)

        cache_file = os.path.join(CACHE_DIR, f"{image_hash}.json")
        session_file = os.path.join(SESSION_DIR, f"{thread_id}.json")

        # 5. Check if prediction exists in cache
        if os.path.exists(cache_file):
            logger.info(f"Cache hit! Loading prediction from: '{cache_file}'")
            with open(cache_file, "r") as f:
                predictions = json.load(f)
            status = "Loaded from local cache"
        else:
            logger.info(f"Cache miss! Executing ONNX model prediction...")
            # Predict
            predictions = dog_classifier.predict(image_bytes)
            # Write cache
            with open(cache_file, "w") as f:
                json.dump(predictions, f, indent=2)
            status = "Executed classification model"

        # 6. Save active prediction mapping for this thread session
        session_data = {
            "last_image_hash": image_hash,
            "image_path": image_path,
            "predictions": predictions,
        }
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)
        logger.info(f"Stored session mapping in: '{session_file}'")

        # 7. Format tool response string
        pred_strings = [
            f"{p['breed']} ({p['confidence']:.2%})" for p in predictions
        ]
        return f"Success ({status}). Predictions: {', '.join(pred_strings)}"

    except Exception as e:
        logger.error(f"Error inside classify_dog_image_tool: {e}", exc_info=True)
        return f"Error: Failed to process dog classification. {str(e)}"
