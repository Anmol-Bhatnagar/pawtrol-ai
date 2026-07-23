import io
from unittest.mock import patch
from fastapi.testclient import TestClient
from PIL import Image


def test_dogs_classify_unauthorized(client: TestClient) -> None:
    """
    Verifies that classification uploads are blocked without a secure token header.
    """
    response = client.post(
        "/api/v1/dogs/classify",
        files={"file": ("dog.jpg", b"fakeimgdata", "image/jpeg")},
    )
    assert response.status_code == 401


def test_dogs_classify_file_size_limit(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """
    Verifies that uploading a payload greater than 5MB triggers a 400 Bad Request.
    """
    # 6MB of dummy bytes
    oversized_data = b"X" * (6 * 1024 * 1024)
    response = client.post(
        "/api/v1/dogs/classify",
        files={"file": ("dog.jpg", oversized_data, "image/jpeg")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "exceeds maximum allowed upload size" in response.json()["detail"]


def test_dogs_classify_invalid_image_format(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """
    Verifies that uploading text files or corrupt files is blocked.
    """
    corrupt_data = b"arbitrary-non-image-text-stream"
    response = client.post(
        "/api/v1/dogs/classify",
        files={"file": ("dog.txt", corrupt_data, "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "not a valid image" in response.json()["detail"]


@patch("src.services.dog_classifier.dog_classifier.predict")
def test_dogs_classify_successful_run(
    mock_predict: patch, client: TestClient, auth_headers: dict[str, str]
) -> None:
    """
    Verifies that valid images are processed successfully and predictions match our schema.
    """
    # Mock prediction result
    mock_predict.return_value = [
        {"breed": "pug", "confidence": 0.88},
        {"breed": "beagle", "confidence": 0.08},
    ]

    # Create dummy JPEG image bytes
    img = Image.new("RGB", (200, 200), color=(240, 240, 240))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    img_bytes = buf.getvalue()

    response = client.post(
        "/api/v1/dogs/classify",
        files={"file": ("dog.jpg", img_bytes, "image/jpeg")},
        headers=auth_headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert "predictions" in payload
    assert len(payload["predictions"]) == 2
    assert payload["predictions"][0]["breed"] == "pug"
    assert payload["predictions"][0]["confidence"] == 0.88
    assert "latency_seconds" in payload
