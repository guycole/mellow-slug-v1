import slug_app


def test_execute_runs_validator_mode(monkeypatch) -> None:
    class FakeValidator:
        def __init__(self, _logger, _postgres):
            pass

        def execute(self) -> int:
            return 0

    monkeypatch.setattr(slug_app, "SlugValidator", FakeValidator)

    app = slug_app.SlugApp("validator")

    assert app.execute() == 0


def test_execute_rejects_invalid_mode() -> None:
    app = slug_app.SlugApp("bad-mode")

    assert app.execute() == 1
