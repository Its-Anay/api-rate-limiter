import pytest
import redis as redis_sync
from starlette.testclient import TestClient
from app.main import app

VALKEY_URL = "redis://localhost:6379"
RATE_LIMIT_KEY = "rate_limit:testclient"

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_redis():
    r = redis_sync.from_url(VALKEY_URL, decode_responses=True)
    keys = r.keys("rate_limit:*")
    if keys:
        r.delete(*keys)
    yield r
    keys = r.keys("rate_limit:*")
    if keys:
        r.delete(*keys)
    r.close()


def test_valid_requests_get_200():
    for _ in range(5):
        response = client.get("/")
        assert response.status_code == 200


def test_sixth_request_gets_429():
    for _ in range(5):
        client.get("/")
    response = client.get("/")
    assert response.status_code == 429


def test_after_window_passes_get_200_again(clean_redis):
    for _ in range(5):
        client.get("/")
    assert client.get("/").status_code == 429

    # Simulate window passing: delete the rate limit keys so the bucket resets
    keys = clean_redis.keys("rate_limit:*")
    if keys:
        clean_redis.delete(*keys)

    response = client.get("/")
    assert response.status_code == 200
