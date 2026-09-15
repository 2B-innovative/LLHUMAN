# LLHUMAN

**Don't believe in AI? Run a Large Language Human instead.**

LLHUMAN exposes an OpenAI-compatible chat-completions endpoint, except the model is a real human sitting in a browser.

Clients send requests to `/v1/chat/completions`. The request appears in the operator console over WebSocket. A human reads the conversation, thinks for an unpredictable amount of time, types a response, and LLHUMAN returns it in an OpenAI-style response object.

No GPUs. No tensor cores. No quantization. Just one highly overparameterized biological model with approximately 86 billion neurons and wildly inconsistent uptime.

> Latency may vary. Context window depends on caffeine. Hallucinations predate computers.

## Features

- OpenAI-style `POST /v1/chat/completions`
- OpenAI-style `GET /v1/models`
- Browser-based human operator console
- WebSocket delivery of incoming prompts
- Optional API key for clients
- Optional operator token
- Docker / Docker Compose setup
- `coffee_tokens` usage metric
- No CUDA required
- Native multimodal support if the operator looks at another screen
- RLHF available through salary, praise, snacks, and mild peer pressure

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

## Completely fictional benchmarks

The following benchmark results are invented for entertainment and should not be cited in a paper, procurement process, investor deck, benchmark leaderboard, regulatory filing, or argument on Hacker News.

| Model | MMLU | HumanEval | TruthfulQA | CoffeeEval | MeetingBench | Median latency | P99 latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `human-1-rested` | 71.4 | 58.2 | 63.7 | 96.1 | 12.0 | 18 s | 4 min |
| `human-1-senior-dev` | 66.0 | 91.3 | 59.8 | 88.4 | 7.2 | 42 s | 17 min |
| `human-1-after-lunch` | 54.8 | 51.0 | 61.2 | 99.2 | 3.1 | 2 min | 48 min |
| `human-1-friday-16-30` | 39.5 | 44.0 | 74.1 | 100.0 | 0.4 | 7 min | Monday |
| `human-1-manager` | 82.0* | 14.0 | 68.9 | 91.0 | 99.7 | 11 s | 2 h |

`*` Self-reported.

### Latency profile

Unlike conventional LLMs, LLHUMAN offers genuinely non-deterministic latency at infrastructure level:

```text
P50   18 seconds
P90   4 minutes
P95   "one sec"
P99   after this meeting
P99.9 tomorrow morning
max   forgotten entirely
```

Cold starts may occur after sleep, weekends, annual leave, lunch, context switches, or opening Slack.

### Throughput

Typical sustained throughput for one replica:

```text
Input:   ~200-600 words/minute reading speed
Output:  ~30-90 words/minute typing speed
Peak:    significantly higher while arguing online
Batching: supported, strongly discouraged
Concurrency: technically >1, quality degrades rapidly
```

Horizontal scaling is available by hiring more humans.

## Pricing

LLHUMAN uses a radically transparent pricing model based on actual biological compute.

Estimated hosted inference cost for one operator:

| Cost component | Approximate price |
| --- | ---: |
| Electricity | negligible |
| Coffee | €0.20-€4.50 / request |
| Lunch amortization | €3-€15 / day |
| Salary | alarmingly non-zero |
| Office chair | capex |
| Context-switch penalty | unbounded |
| GPU | €0 |
| Existential dread | included |

A rough enterprise calculation may result in token prices several orders of magnitude above frontier LLM APIs, especially if the human insists on employment law, weekends, or ergonomics.

Volume discounts are available by lowering expectations.

## Model card

**Model:** `human-1`

**Architecture:** carbon-based recurrent biological network

**Parameters:** unknown; inspection voids warranty

**Context window:** approximately 3-7 active thoughts, plus whatever is written down

**Training cutoff:** continuously updated, inconsistently indexed

**Fine-tuning:** possible, usually takes years

**Quantization:** not recommended

**Temperature:** typically 36.5-37.5 °C

**Tool use:** excellent when the tool has buttons

**Function calling:** supported if instructions are sufficiently explicit

**Vision:** generally strong, degrades without corrective lenses

**Audio:** native

**Long-term memory:** surprisingly good for embarrassing events, unreliable for passwords

**Catastrophic forgetting:** common after walking into another room

**Safety alignment:** varies by operator, jurisdiction, incentives, sleep, and whether the request arrives before coffee

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

## Tests

Install dev dependencies and run:

```bash
pip install -r requirements-dev.txt
pytest -q
```

The smoke tests check the model-list shape, chat-completion response shape, API-key enforcement, and the no-human-online failure mode.

GitHub Actions runs them automatically on pushes and pull requests.

## Current limitations

This is intentionally tiny. At the moment:

- one process keeps requests in memory;
- any connected operator can answer any pending request;
- streaming is not implemented because humans mostly stream through speech, not HTTP chunks;
- token counts are fake, because counting human thoughts remains an unsolved observability problem;
- restarting the server forgets pending inference jobs, much like a human entering another room;
- autoscaling requires recruiting;
- high availability may require two humans who are awake at the same time;
- deterministic output cannot be guaranteed, including when repeating the exact same prompt to the exact same operator five minutes later.

## Why?

Mostly because it is funny.

But it is also a useful tiny test double for human-in-the-loop systems: anything that speaks an OpenAI-style chat-completions API can, in principle, be powered by a person instead of an LLM.

It may also finally settle whether your agent framework actually requires intelligence, or merely something willing to return JSON eventually.

## License

MIT
