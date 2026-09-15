import json

from fastapi.testclient import TestClient

from app.main import app, operators, pending


class FakeHuman:
    async def send_text(self, message: str) -> None:
        payload = json.loads(message)
        request_id = payload["request_id"]
        pending[request_id].set_result("Biological inference complete.")


client = TestClient(app)


def setup_function() -> None:
    operators.clear()
    pending.clear()


def teardown_function() -> None:
    operators.clear()
    pending.clear()


def test_models_shape(monkeypatch) -> None:
    monkeypatch.delenv("LLHUMAN_API_KEY", raising=False)

    response = client.get("/v1/models")

    assert response.status_code == 200
    body = response.json()
    assert body["object"] == "list"
    assert body["data"][0]["id"] == "human-1"
    assert body["data"][0]["object"] == "model"


def test_chat_completion_openai_shape(monkeypatch) -> None:
    monkeypatch.delenv("LLHUMAN_API_KEY", raising=False)
    operators.add(FakeHuman())

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "human-1",
            "messages": [
                {"role": "user", "content": "Are you sentient?"},
            ],
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["id"].startswith("chatcmpl-human-")
    assert body["object"] == "chat.completion"
    assert isinstance(body["created"], int)
    assert body["model"] == "human-1"

    choice = body["choices"][0]
    assert choice["index"] == 0
    assert choice["message"] == {
        "role": "assistant",
        "content": "Biological inference complete.",
    }
    assert choice["finish_reason"] == "stop"

    assert body["usage"]["prompt_tokens"] == 0
    assert body["usage"]["completion_tokens"] == 0
    assert body["usage"]["total_tokens"] == 0
    assert body["usage"]["coffee_tokens"] == 1


def test_no_human_returns_503(monkeypatch) -> None:
    monkeypatch.delenv("LLHUMAN_API_KEY", raising=False)

    response = client.post(
        "/v1/chat/completions",
        json={
            "model": "human-1",
            "messages": [{"role": "user", "content": "Hello?"}],
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "No human model is currently online."


def test_api_key_is_enforced(monkeypatch) -> None:
    monkeypatch.setenv("LLHUMAN_API_KEY", "very-secret-human")

    unauthorized = client.get("/v1/models")
    authorized = client.get(
        "/v1/models",
        headers={"Authorization": "Bearer very-secret-human"},
    )

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
