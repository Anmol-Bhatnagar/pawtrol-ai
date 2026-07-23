import os
import pytest
from typing import Generator

# Override configuration variables before importing any app modules
os.environ["ENVIRONMENT"] = "testing"
os.environ["API_KEY"] = "test-secret-key-123"
os.environ["OPENAI_API_KEY"] = "mock-openai-key"

from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Initializes a test client with FastAPI application context.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def auth_headers() -> dict[str, str]:
    """
    Supplies authentication headers containing test credentials.
    """
    return {"X-API-Key": "test-secret-key-123"}
