import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.state.store import state

@pytest.fixture(autouse=True)
def reset_state():
    state.reset(); yield; state.reset()

@pytest.fixture
def client(): return TestClient(app)
