from fastapi.testclient import TestClient


def test_chat_unauthorized(client: TestClient) -> None:
    """
    Validates requests missing security keys are blocked with 401 Unauthorized.
    """
    payload = {"messages": [{"role": "user", "content": "Hello!"}]}
    response = client.post("/api/v1/chat/completions", json=payload)
    assert response.status_code == 401


def test_chat_authorized_direct_response(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """
    Verifies regular conversation requests bypass search triggers and get standard completions.
    """
    payload = {"messages": [{"role": "user", "content": "Hello agent"}]}
    response = client.post(
        "/api/v1/chat/completions", json=payload, headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert "received your request" in data["message"]["content"]
    assert "messages_count" in data["metadata"]


def test_chat_authorized_search_trigger(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    """
    Verifies that mentioning search terms invokes the search flow correctly in the backend.
    """
    payload = {
        "messages": [
            {
                "role": "user",
                "content": "Please search for python FastAPI examples.",
            }
        ]
    }
    response = client.post(
        "/api/v1/chat/completions", json=payload, headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert data["message"]["role"] == "assistant"
    assert "search tool" in data["message"]["content"].lower()
    assert "FastAPI" in data["message"]["content"]
