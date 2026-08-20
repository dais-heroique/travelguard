from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "scripts" / "generate_native_ios.py").read_text(encoding="utf-8")
assert "positionTask?.cancel()" in source
assert "requestCompletedAt = Date()" in source
assert "schemaVersion == 1" in source
assert "cacheMaxAge" in source
assert "options: [.atomic]" in source
assert "RiskPlace.inViewport(region, risks: store.risks)" in source
assert "let limit = lonDelta > 60 || latDelta > 60 ? 80" in source
assert "sourceSignal: Int" in source
assert "INCONNUE" in source
assert "Prix probablement abusif" in source
assert "protectionStatusLabel" in source
print("audit 24 deterministic checks: OK")
