from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "scripts/generate_native_ios.py").read_text(encoding="utf-8")
assert "risk.alertRadius.isFinite" in source
assert "(1...5000).contains(risk.alertRadius)" in source
assert "ids.insert(risk.id).inserted" in source
assert "Set(risk.evidence.map(\\.id)).count == risk.evidence.count" in source
assert "locationPrecision == .point" in source
assert "sourceRecord" in source
assert "endpoint.scheme?.lowercased() == \"https\"" in source
assert "allowedHost" in source
assert "maxResponseBytes" in source
assert "data.count <= maxResponseBytes" in source
assert "Content-Type" in source
assert "If-None-Match" in source
assert "statusCode == 304" in source
assert "for delay in [0.0, 1.0, 3.0, 10.0]" in source
assert "bestByCell" in source
assert "candidateRelevance" in source
assert "manager.stopMonitoring(for: region)" in source
print("audit 27 deterministic checks: OK")
