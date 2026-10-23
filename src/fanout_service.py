from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient


@dataclass(frozen=True)
class AssetPublished:
    player_id: str
    asset_id: str
    title: str
    subscribers: tuple[str, ...]


def notification_payloads(event: AssetPublished) -> list[dict[str, Any]]:
    """Create one notification per subscriber, preserving event identity."""
    return [
        {
            "kind": "asset_published",
            "asset_id": event.asset_id,
            "player_id": event.player_id,
            "title": event.title,
            "subscriber_id": subscriber,
        }
        for subscriber in event.subscribers
    ]


def fan_out(event: AssetPublished, client: InfraiClient) -> int:
    """Publish notifications and return the number accepted by the queue."""
    sent = 0
    for payload in notification_payloads(event):
        client.publish(payload)
        sent += 1
    return sent
