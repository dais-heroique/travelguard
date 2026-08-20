from pathlib import Path
import plistlib
import re

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "native-package"
SRC = NATIVE / "TravelGuard"

required = [
    SRC / "Models.swift",
    SRC / "Services.swift",
    SRC / "RiskMapView.swift",
    SRC / "ScannerView.swift",
    SRC / "SafetyView.swift",
    SRC / "Info.plist",
]
for path in required:
    assert path.exists(), f"missing native file: {path}"

all_swift = "\n".join(path.read_text(encoding="utf-8") for path in SRC.glob("*.swift"))
assert "let trustedRisks: [RiskPlace] = []" in all_swift
assert "sampleRisks" not in all_swift
assert "demoRisks" not in all_swift
assert "samplePrices" not in all_swift
assert "Donnée locale de démonstration" not in all_swift
assert "OfficialSource" in all_swift
assert "recognitionLanguages" in all_swift
assert "calculatedTotal" in all_swift
assert "formattedDistance" in all_swift
assert "horizontalAccuracy > 100" in all_swift
assert "hasFreshLocationForAlerts" in all_swift
assert "horizontalAccuracy <= 200" in all_swift
assert "refreshMonitoredRegions" in all_swift
assert "updateRisks" in all_swift
assert "CLError" in all_swift
assert "pausesLocationUpdatesAutomatically = true" in all_swift
assert "monitoringScore" in all_swift
assert "serverReliabilityIndex" in all_swift
assert "sourceId" in all_swift
assert "bbox" in all_swift
assert "pageSize" in all_swift
assert "requestViewportRisks" in all_swift
assert "analysisGeneration" in all_swift
assert "monitoringActive" in all_swift
assert "isUsingCachedLocation" in all_swift
assert "distanceFilter = 100" in all_swift
assert "startUpdatingLocation" not in all_swift
assert "waitingForAlwaysAuthorization" not in all_swift
assert "store.risks" in all_swift
assert "Hashable, Codable" in all_swift
assert "RiskPlace.validated" in all_swift
assert "riskCacheURL" in all_swift
assert "RiskCacheEnvelope" in all_swift
assert "Data(contentsOf:" in all_swift
assert "options: [.atomic]" in all_swift
assert "beginRiskSync" in all_swift
assert "notificationCooldown" in all_swift
assert "cachedAgeLabel" in all_swift
assert "geocodingErrorMessage" in all_swift
assert "zone visible" in all_swift
assert "MKMapRect" in all_swift
assert "inViewport" in all_swift
assert "positionSearchTimedOut" in all_swift
assert "positionTask?.cancel()" in all_swift
assert "requestCompletedAt" in all_swift
assert "schemaVersion == 1" in all_swift
assert "cacheMaxAge" in all_swift
assert "protectionStatusLabel" in all_swift
assert "Prix potentiellement abusif" in all_swift
assert "INCONNUE" in all_swift
assert "sourceSignal" in all_swift
assert ".prefix(300)" not in all_swift
assert "riskDataFreshnessLabel" in all_swift
assert "riskDataIsStale" in all_swift
assert "frame(width: 44, height: 44)" in all_swift
assert "location.horizontalAccuracy > 200" in all_swift
assert "manager.monitoredRegions.forEach { manager.stopMonitoring" in all_swift
assert "settings.authorizationStatus != .authorized" in all_swift
assert "isUsingCachedLocation { store.location.refresh(); return }" in all_swift
assert "hasUserInteractedWithMap" in all_swift
assert "!hasUserInteractedWithMap" in all_swift
assert "UIApplication.openSettingsURLString" in all_swift
assert "requestAlwaysAuthorization" in all_swift
assert ".prefix(20)" in all_swift
assert "canOpenURL" in all_swift
assert "countryCode" in all_swift
assert "onMapCameraChange" in all_swift
assert "simultaneousGesture" not in all_swift
assert "padding(.top, -52)" not in all_swift
assert "latitude: 0, longitude: 0" in all_swift
assert "> 200" in all_swift
assert "Aucune référence officielle" in all_swift
assert re.search(r"https://travel\.state\.gov/.+scams", all_swift)

info = plistlib.loads((SRC / "Info.plist").read_bytes())
for key in ("CFBundleIdentifier", "CFBundleExecutable", "CFBundlePackageType", "NSCameraUsageDescription", "NSLocationWhenInUseUsageDescription", "NSLocationAlwaysAndWhenInUseUsageDescription"):
    assert key in info, f"missing Info.plist key: {key}"

project = (NATIVE / "TravelGuard.xcodeproj" / "project.pbxproj").read_text(encoding="utf-8")
assert "com.daisheroique.travelguard" in project
assert "isa = PBXFileReference" in project
assert "INFOPLIST_FILE" in project

print("native quality checks: OK")
