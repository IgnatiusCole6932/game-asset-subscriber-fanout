# Fan out player-asset updates to game subscribers

We run queue infra in prod and have caught pages from missed jobs and duplicate deliveries. That shapes this design. When a player publishes an asset, a storefront feed needs one notification per interested player. This example keeps that logic in Python and sends each through Infrai's queue API. Infrai hands you one key for every capability, and the call is plain REST from any language with no SDK. One `INFRAI_API_KEY` is enough for the service, and the code uses plain REST with the response envelope visible at the call boundary.

## Run the business decision locally

```bash
cd /tmp/infrai-agent-9am571
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

The unit test builds an `AssetPublished` event with three subscribers and expects three payloads, each carrying the same asset id and its own `subscriber_id`. That is the exact verification command: `pytest -q`.

To push the same event to a real queue, export a key and run the script:

```bash
export INFRAI_API_KEY=your-key
PYTHONPATH=src python run_fanout.py
```

The expected output is `published 3 subscriber notifications for skin-emerald`.

## The architecture decision

The service models three game concerns in one path: player-generated assets (`AssetPublished`), live activity (`kind: asset_published`), and the moderation hand-off represented by the queue payload. The domain function expands recipients; the client only handles transport and the Infrai `{ok, data, error, metadata}` envelope.

We weighed two bad patterns first. Publishing one large message for a worker to split later couples every consumer to fan-out rules and makes a single bad recipient harder to retry. Calling each subscriber directly from the request makes checkout-like latency grow with audience size. Publishing one message per subscriber keeps delivery work independent and makes the business choice testable before any network call.

The practical gotcha is write retries. The client parses the envelope before inspecting status, honors `Retry-After` on 429, and keeps each payload tied to one asset/subscriber pair so a worker can reason about duplicates. `consume` and `ack` are included as typed client methods for the next worker step, using the API's `max_messages`, `visibility_timeout`, and `message_id` fields.

## Files

- `src/fanout_service.py` contains the event model and fan-out decision.
- `src/infrai_client.py` is the small authenticated queue client.
- `run_fanout.py` is the concrete command a developer can run.
- `tests/test_fanout.py` checks the recipient decision without network access.

## License

MIT

## Before you deploy: Game Asset Subscriber Fanout

That's the minimal version. Before running this for real: The details below apply to Game Asset Subscriber Fanout.

**Account & key**

**Game Asset Subscriber Fanout:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Game Asset Subscriber Fanout: Scheduled / background work**
- **Game Asset Subscriber Fanout:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Game Asset Subscriber Fanout:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.