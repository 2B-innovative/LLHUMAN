import asyncio
import json
import os
import time
import uuid
from typing import Any

from fastapi import FastAPI, Header, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

app = FastAPI(title="LLHUMAN", version="0.1.0")


class Message(BaseModel):
    role: str
    content: Any


class ChatCompletionRequest(BaseModel):
    model: str = "human-1"
    messages: list[Message]
    stream: bool = False
    temperature: float | None = None
    max_tokens: int | None = None


class HumanReply(BaseModel):
    request_id: str
    content: str = Field(min_length=1)


pending: dict[str, asyncio.Future[str]] = {}
operators: set[WebSocket] = set()


def require_api_key(authorization: str | None) -> None:
    api_key = os.getenv("LLHUMAN_API_KEY")
    if not api_key:
        return
    if authorization != f"Bearer {api_key}":
        raise HTTPException(status_code=401, detail="Invalid API key")


async def broadcast(payload: dict[str, Any]) -> None:
    message = json.dumps(payload)
    dead: list[WebSocket] = []
    for websocket in operators:
        try:
            await websocket.send_text(message)
        except Exception:
            dead.append(websocket)
    for websocket in dead:
        operators.discard(websocket)


@app.get("/")
async def operator_ui() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/health")
async def health() -> dict[str, Any]:
    return {"status": "ok", "operators": len(operators), "pending": len(pending)}


@app.get("/v1/models")
async def models(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    require_api_key(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": "human-1",
                "object": "model",
                "created": 0,
                "owned_by": "humanity",
            }
        ],
    }


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatCompletionRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    require_api_key(authorization)
    if request.stream:
        raise HTTPException(status_code=400, detail="Streaming is not supported yet. Humans type in bursts.")
    if not operators:
        raise HTTPException(status_code=503, detail="No human model is currently online.")

    request_id = f"chatcmpl-human-{uuid.uuid4().hex}"
    future: asyncio.Future[str] = asyncio.get_running_loop().create_future()
    pending[request_id] = future

    await broadcast(
        {
            "type": "request",
            "request_id": request_id,
            "model": request.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }
    )

    try:
        answer = await asyncio.wait_for(
            future,
            timeout=float(os.getenv("HUMAN_TIMEOUT_SECONDS", "900")),
        )
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="The human model timed out.") from exc
    finally:
        pending.pop(request_id, None)

    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": request.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": answer},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "coffee_tokens": 1,
        },
    }


@app.websocket("/ws/operator")
async def operator_socket(websocket: WebSocket) -> None:
    operator_token = os.getenv("OPERATOR_TOKEN")
    if operator_token and websocket.query_params.get("token") != operator_token:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    operators.add(websocket)
    await websocket.send_json({"type": "connected", "pending": len(pending)})

    try:
        while True:
            data = await websocket.receive_json()
            reply = HumanReply.model_validate(data)
            future = pending.get(reply.request_id)
            if future is None or future.done():
                await websocket.send_json(
                    {"type": "error", "message": "Request is no longer pending."}
                )
                continue
            future.set_result(reply.content)
            await websocket.send_json(
                {"type": "accepted", "request_id": reply.request_id}
            )
    except WebSocketDisconnect:
        operators.discard(websocket)
