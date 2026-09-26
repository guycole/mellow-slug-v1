import logging

from validator import SlugValidator


class FakePostgres:
    def __init__(self):
        self.selected = None
        self.inserted = []
        self.daily_scores = []

    def load_log_select_by_file_name(self, file_name):
        return self.selected

    def load_log_insert(self, load_log):
        self.inserted.append(load_log)

    def geo_loc_select_by_site(self, site_name):
        class GeoLocCandidate:
            id = 42

        return [GeoLocCandidate()]

    def daily_score_insert_or_update(self, daily_score):
        self.daily_scores.append(daily_score)


def _validator() -> tuple[SlugValidator, FakePostgres]:
    postgres = FakePostgres()
    validator = SlugValidator(logging.getLogger("test"), postgres)
    return validator, postgres


def test_load_log_test_inserts_when_not_previously_processed() -> None:
    validator, postgres = _validator()
    validator.json_helper.raw_json = {
        "crateName": "wombat04",
        "timeStamp": {"epochSeconds": 1, "iso8601": "1970-01-01T00:00:01+00:00"},
        "equipment": {"hostName": "host-a"},
        "geoLoc": {"siteName": "vallejo01"},
        "receiver": {"task": "slug-v1"},
        "observations": [],
        "job": {"project": "slug-v1"},
    }

    result = validator.load_log_test("abc.json")

    assert result is True
    assert len(postgres.inserted) == 1
    assert postgres.inserted[0]["file_name"] == "abc.json"
    assert postgres.inserted[0]["epoch_seconds"] == 1
    assert postgres.inserted[0]["geo_loc_id"] == 42
    assert len(postgres.daily_scores) == 1
    assert postgres.daily_scores[0]["file_quantity"] == 1


def test_file_processor_success_path(monkeypatch) -> None:
    validator, _postgres = _validator()
    monkeypatch.setattr(validator.json_helper, "json_file_tester", lambda _name: True)
    monkeypatch.setattr(validator, "load_log_test", lambda _name: True)

    calls = {"success": 0, "failure": 0}
    monkeypatch.setattr(validator, "file_success", lambda _name: calls.__setitem__("success", calls["success"] + 1))
    monkeypatch.setattr(validator, "file_failure", lambda _name: calls.__setitem__("failure", calls["failure"] + 1))

    result = validator.file_processor("ok.json")

    assert result is True
    assert calls["success"] == 1
    assert calls["failure"] == 0


def test_execute_processes_all_targets(monkeypatch) -> None:
    validator, _postgres = _validator()

    monkeypatch.setattr("validator.os.chdir", lambda _path: None)
    monkeypatch.setattr("validator.os.listdir", lambda _path: ["b.json", "a.json"])

    seen = []
    monkeypatch.setattr(validator, "file_processor", lambda name: seen.append(name) or True)

    result = validator.execute()

    assert result == 0
    assert seen == ["a.json", "b.json"]
