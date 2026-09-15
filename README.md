# LLHUMAN

**Don't believe in AI? Run a Large Language Human instead.**

LLHUMAN exposes an OpenAI-compatible chat-completions endpoint, except the model is a real human sitting in a browser.

Clients send requests to `/v1/chat/completions`. The request appears in the operator console over WebSocket. A human reads the conversation, types a response, and LLHUMAN returns it in an OpenAI-style response object.

Latency may vary. Context window depends on caffeine.

## Features

- OpenAI-style `POST /v1/chat/completions`
- OpenAI-style `GET /v1/models`
- Browser-based human operator console
- WebSocket delivery of incoming prompts
- Optional API key for clients
- Optional operator token
- Docker / Docker Compose setup
- `coffee_tokens` usage metric

## Architecture

```text
OpenAI client / agent
        |
        | POST /v1/chat/completions
        v
+-------------------+
|      LLHUMAN      |
|      FastAPI      |
+-------------------+
        |
        | WebSocket
        v
+-------------------+
| Operator Console  |
|      Human        |
+-------------------+
        |
        | biological inference
        v
 OpenAI-style response
```

## Quick start

```bash
git clone https://github.com/2B-innovative/LLHUMAN.git
cd LLHUMAN
cp .env.example .env
docker compose up --build
```

Then open:

```text
http://localhost:8000
```

Enter the operator token from `.env` and click **Connect human**.

## Use it with the OpenAI Python SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="change-me-too",
)

response = client.chat.completions.create(
    model="human-1",
    messages=[
        {"role": "system", "content": "You are a helpful biological intelligence."},
        {"role": "user", "content": "Explain Kubernetes in one paragraph."},
    ],
)

print(response.choices[0].message.content)
```

The HTTP request waits until a human answers or `HUMAN_TIMEOUT_SECONDS` is reached.

## curl example

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer change-me-too" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "human-1",
    "messages": [
      {"role": "user", "content": "Are humans AGI?"}
    ]
  }'
```

Example response:

```json
{
  "id": "chatcmpl-human-...",
  "object": "chat.completion",
  "model": "human-1",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "It depends who you ask."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0,
    "coffee_tokens": 1
  }
}
```

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `OPERATOR_TOKEN` | Protects the human operator WebSocket | empty |
| `LLHUMAN_API_KEY` | Bearer token for `/v1/*` | empty |
| `HUMAN_TIMEOUT_SECONDS` | Maximum biological inference time | `900` |

For anything exposed to the internet, set both tokens and put LLHUMAN behind HTTPS.

## Current limitations

This is intentionally tiny. At the moment:

- one process keeps requests in memory;
- any connected operator can answer any pending request;
- streaming is not implemented;
- token counts are fake, because counting human thoughts remains an unsolved problem;
- restarting the server forgets pending inference jobs, much like a human entering another room.

## Why?

Mostly because it is funny.

But it is also a useful tiny test double for human-in-the-loop systems: anything that speaks an OpenAI-style chat-completions API can, in principle, be powered by a person instead of an LLM.

## License

MIT
