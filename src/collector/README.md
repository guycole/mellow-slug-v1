## Collector Blueprint For Other Projects

This collector is a minimal template for producing timestamped JSON payload files into a fresh-ingest directory. The intent is to keep a stable pipeline contract while allowing each project to provide its own observation collection logic.

### Core Design

1. Uses Pydantic models to define payload sections: equipment, geoLoc, job, receiver, timeStamp, and observations.
2. Generates UTC timestamps from epoch seconds automatically.
3. Uses an abstract collector interface (`get_observations`, `execute`) to standardize implementation.
4. Builds output file names with UUID values to avoid collisions.
5. Writes one JSON file per execution to `freshDir`.
6. Reads runtime configuration from YAML (`config.yaml` by default).

### Execution Flow

1. Load YAML config.
2. Instantiate typed model objects from config fields.
3. Derive job metadata (`mode`, `project`, `task`) from receiver/task context.
4. Collect observations (no-op in this project).
5. Build the final slug payload.
6. Serialize formatted JSON to `freshDir/<uuid>.json`.

Note: The empty observations list is intentional because this is an example application. A real collector should include domain-specific logic to gather and process observations before payload generation.

### Required Configuration Contract

The collector expects these keys in `config.yaml`:

1. `crateName`
2. `freshDir`
3. `equipment.hostName`
4. `equipment.hostType`
5. `geoLoc.altitude`
6. `geoLoc.latitude`
7. `geoLoc.longitude`
8. `geoLoc.siteName`
9. `receiver.antenna`
10. `receiver.receiverId`
11. `receiver.task`
12. `receiver.type`

### Output Payload Contract

Each emitted JSON file contains:

1. `crateName`
2. `fileName`
3. `version`
4. `equipment`
5. `geoLoc`
6. `job`
7. `receiver`
8. `timeStamp` (`epochSeconds`, `iso8601`)
9. `observations`

### Integration Pattern

1. `bootboy.py` generates `config.yaml` from host/admin metadata.
2. `collector.sh` activates the venv and executes `collector.py` on a schedule.
3. Downstream validation ingests files from `freshDir` and enforces schema and idempotency rules.

### Testing With Pytest

Pytest tests for this collector live in the same directory as `collector.py`.

Run tests from `src/collector/pytest.sh`

### Reuse Guidance

To create a new collector project with the same features:

1. Copy this collector structure and keep the model + execution flow intact.
2. Replace `get_observations()` with domain-specific collection logic.
3. Keep output JSON shape compatible with the validator schema.
4. Keep config generation and scheduling wrappers (BootBoy + shell runner).
5. Add tests for schema conformance and duplicate file handling.

### Known Compatibility Notes

1. Current no-op observations are empty; if populated, observation items must match validator schema fields.
2. Validation currently checks for project value `slug-v1`; adjust validator rules when cloning for new projects.
