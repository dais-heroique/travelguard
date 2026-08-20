from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "scripts/generate_native_ios.py").read_text(encoding="utf-8")
native = "\n".join(p.read_text(encoding="utf-8") for p in (root / "native-package/TravelGuard").glob("*.swift"))
assert "protocol RiskRepository" in source
assert "RemoteRiskRepository" in source
assert "RiskFeedURL" in source
assert "riskCacheURL: URL = FileManager.default.urls(for: .applicationSupportDirectory" in source
assert "travelguard-risks-v2.json" in source
assert "schemaVersion == 2" in source
assert "risk.revokedAt == nil" in source
assert "sourceType: SourceTrust" in source
assert "RiskEvidence" in source
assert "risk.alertRadius" in source
assert "if occupiedCells.insert(cell).inserted" in source
assert "|| risk.score >= 80" not in source
assert "radius: 250" not in source
assert "manager.stopMonitoring(for: region)" in source
assert "risk.reliabilityLabel" in source
assert "for match in matches" in source
assert "INCONNUE" in source
assert "Prix probablement abusif" in source
assert "Resultat limité au document" not in native
assert "sourceSignal" in native
assert "Aucune donnée de risque ou de prix n’est embarquée" in native
print("audit 26 deterministic checks: OK")
