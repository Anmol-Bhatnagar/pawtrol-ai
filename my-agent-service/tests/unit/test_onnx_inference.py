import io
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image
from src.services.dog_classifier import DogBreedClassifier


def test_preprocess_image_transforms() -> None:
    """
    Validates that images are correctly resized, center cropped,
    and transposed to shape (1, 3, 224, 224).
    """
    classifier = DogBreedClassifier()
    # Create a test tall image
    test_img = Image.new("RGB", (300, 450), color=(100, 150, 200))
    tensor = classifier.preprocess_image(test_img)

    assert isinstance(tensor, np.ndarray)
    assert tensor.shape == (1, 3, 224, 224)
    # Check data range is normalized (around mean/std deviation)
    assert not np.allclose(tensor, 0)


@patch("onnxruntime.InferenceSession")
def test_predict_mapping_flow(mock_session_class: MagicMock) -> None:
    """
    Verifies that class logits are correctly sorted, mapped,
    and normalized using Softmax.
    """
    # 1. Setup session mocks
    mock_session = MagicMock()
    mock_session.get_inputs.return_value = [
        MagicMock(name="input", type="tensor(float)")
    ]
    # Simulated logits: highest weight for index 1 ('beagle')
    mock_session.run.return_value = [
        np.array([[0.5, 4.0, -1.2]], dtype=np.float32)
    ]
    mock_session_class.return_value = mock_session

    # 2. Configure classifier instance
    classifier = DogBreedClassifier()
    classifier.classes = ["chihuahua", "beagle", "pug"]
    classifier.session = mock_session
    classifier.is_ready = True

    # 3. Build test image bytes
    img = Image.new("RGB", (256, 256), color=(255, 0, 0))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    # 4. Predict
    results = classifier.predict(img_bytes, top_k=2)

    # 5. Assertions
    assert len(results) == 2
    assert results[0]["breed"] == "beagle"
    assert (
        results[0]["confidence"] > 0.90
    )  # Softmax for 4.0 vs 0.5 and -1.2 is high
    assert results[1]["breed"] == "chihuahua"
