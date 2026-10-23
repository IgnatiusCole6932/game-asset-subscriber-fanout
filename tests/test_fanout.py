from fanout_service import AssetPublished, fan_out, notification_payloads


class RecordingClient:
    def __init__(self):
        self.payloads = []

    def publish(self, payload):
        self.payloads.append(payload)
        return {"message_id": f"m-{len(self.payloads)}"}


def test_asset_event_fans_out_once_per_subscriber():
    event = AssetPublished("p1", "a9", "Blue cart", ("s1", "s2", "s3"))
    client = RecordingClient()

    assert fan_out(event, client) == 3
    assert [item["subscriber_id"] for item in client.payloads] == ["s1", "s2", "s3"]
    assert all(item["asset_id"] == "a9" for item in client.payloads)


def test_no_subscribers_means_no_publish():
    assert notification_payloads(AssetPublished("p1", "a9", "Blue cart", ())) == []
