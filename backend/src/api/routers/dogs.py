import io
import logging
import time
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from src.api.dependencies.auth import verify_api_key
from src.api.schemas.dogs import BreedPrediction, ClassificationResponse
from src.services.dog_classifier import dog_classifier

router = APIRouter(prefix="/dogs", tags=["dogs"])
logger = logging.getLogger(__name__)

# Max upload limit: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post(
    "/classify",
    response_model=ClassificationResponse,
    dependencies=[Depends(verify_api_key)],
)
async def classify_dog_image(
    file: UploadFile = File(..., description="Uploaded dog image photo")
) -> ClassificationResponse:
    """
    Accepts multipart dog images, validates formats and sizes,
    and returns sorted breed predictions using ONNX execution.
    """
    t_start = time.perf_counter()

    # 1. Read file bytes and validate size
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        logger.warning(
            f"File upload size validation failed: {file_size} bytes exceeds limit."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds maximum allowed upload size of 5MB (Got: {file_size / (1024 * 1024):.2f}MB).",
        )

    # 2. Verify file content represents a valid image structure using Pillow
    try:
        # Re-open stream since verify closes or invalidates the PIL instance
        img = Image.open(io.BytesIO(content))
        img.verify()

        # Re-verify image loading works to ensure we can decode it fully
        Image.open(io.BytesIO(content))
    except Exception as e:
        logger.warning(f"Image format structure verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image. Supported types: JPEG, PNG, WEBP.",
        )

    # 3. Execute classification through ONNX session
    try:
        predictions = dog_classifier.predict(content)
    except Exception as e:
        logger.error(
            f"Classification service failed: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete image classification due to internal error.",
        )

    latency = time.perf_counter() - t_start
    return ClassificationResponse(
        predictions=[BreedPrediction(**pred) for pred in predictions],
        latency_seconds=latency,
    )
