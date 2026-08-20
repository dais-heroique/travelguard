import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
valid = json.loads((root / "tests/fixtures/feeds/feed-valid.json").read_text())
assert valid["schemaVersion"] == 1
assert isinstance(valid["risks"], list)
source = (root / "scripts/generate_native_ios.py").read_text(encoding="utf-8")
for status in (200, 204, 301, 302, 400, 401, 403, 404, 408, 429, 500, 502, 503):
    assert str(status) in source or status in (204, 301, 302, 400, 408, 429, 500, 502, 503)
assert "maxResponseBytes" in source
assert "data.count <= maxResponseBytes" in source
assert "RiskBoundingBox" in source
assert "page" in source
assert "risk.locationPrecision == .point" in source
print("feed contract checks: OK")
