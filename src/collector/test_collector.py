import json
import uuid

from collector import SlugCollector, TimeStamp


def _config(fresh_dir: str) -> dict[str, object]:
    return {
        "crateName": "demo-crate",
        "freshDir": fresh_dir,
        "equipment": {
            "hostName": "demo-host",
            "hostType": "laptop",
        },
        "geoLoc": {
            "altitude": 100.0,
            "latitude": 42.0,
            "longitude": -71.0,
            "siteName": "demo-site",
        },
        "receiver": {
            "antenna": "dipole",
            "receiverId": 7,
            "task": "slug-v1",
            "type": "wifi",
        },
    }


def test_timestamp_syncs_iso8601_from_epoch_seconds() -> None:
    stamp = TimeStamp(epoch_seconds=0)

    assert stamp.iso8601 == "1970-01-01T00:00:00+00:00"


def test_slug_collector_derives_job_from_receiver_task(tmp_path) -> None:
    collector = SlugCollector(_config(str(tmp_path)))

    assert collector.job.mode == "default"
    assert collector.job.project == "slug-v1"
    assert collector.job.task == "slug-v1"


def test_execute_writes_expected_payload_file(tmp_path, monkeypatch) -> None:
    fixed_uuid = uuid.UUID("5cc9fa9d-5065-400e-b578-76633bdd3699")
    monkeypatch.setattr("collector.uuid.uuid4", lambda: fixed_uuid)

    collector = SlugCollector(_config(str(tmp_path)))
    collector.time_stamp = TimeStamp(epoch_seconds=0)

    result = collector.execute()

    assert result == 0

    output_path = tmp_path / f"{fixed_uuid}.json"
    assert output_path.exists()

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["crateName"] == "demo-crate"
    assert payload["fileName"] == f"{fixed_uuid}.json"
    assert payload["job"]["mode"] == "default"
    assert payload["job"]["project"] == "slug-v1"
    assert payload["timeStamp"]["epochSeconds"] == 0
    assert payload["timeStamp"]["iso8601"] == "1970-01-01T00:00:00+00:00"
    assert payload["observations"] == []