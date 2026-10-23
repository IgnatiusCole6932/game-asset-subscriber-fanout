from fanout_service import AssetPublished, fan_out
from infrai_client import InfraiClient


if __name__ == "__main__":
    event = AssetPublished(
        player_id="player-42",
        asset_id="skin-emerald",
        title="Emerald racer skin",
        subscribers=("player-7", "player-19", "player-88"),
    )
    count = fan_out(event, InfraiClient())
    print(f"published {count} subscriber notifications for {event.asset_id}")
