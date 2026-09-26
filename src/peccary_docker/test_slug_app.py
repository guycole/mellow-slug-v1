import slug_app


def test_execute_runs_loader_mode(monkeypatch) -> None:
    class FakeLoader:
        def __init__(self, _logger, _postgres):
            pass

        def execute(self) -> int:
            return 0

    monkeypatch.setattr(slug_app, "SlugLoader", FakeLoader)

    app = slug_app.SlugApp("loader")

    assert app.execute() == 0


def test_execute_rejects_invalid_mode() -> None:
    app = slug_app.SlugApp("bad-mode")

    assert app.execute() == 1
