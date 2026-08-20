from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = (root / "scripts" / "generate_native_ios.py").read_text(encoding="utf-8")
native = "\n".join(p.read_text(encoding="utf-8") for p in (root / "native-package/TravelGuard").glob("*.swift"))

required = [
    "serverReliabilityIndex",
    "Set(risk.evidence.map(\\.sourceId))",
    "evidenceIsRelated",
    "url.scheme?.lowercased() == \"https\"",
    "risk.sourceRecord?.name == risk.source",
    "RiskPlace.validated(monitoredRisks)",
    ".sorted { $0.score > $1.score }",
    "edgeDistanceScore",
    "startMonitoringSignificantLocationChanges",
    "RiskBoundingBox",
    "pageSize",
    "longitudeSpan",
    "requestViewportRisks",
    "viewportTask?.cancel()",
    "RiskCacheEnvelope",
    "options: [.atomic]",
    "currencyCounts",
    "totalPriority",
    "analysisGeneration",
    "ciContext",
]
missing = [item for item in required if item not in source]
if missing:
    raise SystemExit("missing audit28 markers: " + ", ".join(missing))
assert "RiskPlace.validated(risks)" in native
assert "Prix potentiellement abusif" in native
assert "Prix cohérent" not in native
print("audit 28 deterministic checks: OK")
