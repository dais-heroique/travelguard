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
assert "horizontalAccuracy <= 100" in all_swift
assert "hasUserInteractedWithMap" in all_swift
assert "!hasUserInteractedWithMap" in all_swift
assert "UIApplication.openSettingsURLString" in all_swift
assert "Aucune référence officielle" in all_swift
assert re.search(r"https://travel\.state\.gov/.+scams", all_swift)

info = plistlib.loads((SRC / "Info.plist").read_bytes())
for key in ("CFBundleIdentifier", "CFBundleExecutable", "CFBundlePackageType", "NSCameraUsageDescription", "NSLocationWhenInUseUsageDescription"):
    assert key in info, f"missing Info.plist key: {key}"

project = (NATIVE / "TravelGuard.xcodeproj" / "project.pbxproj").read_text(encoding="utf-8")
assert "com.daisheroique.travelguard" in project
assert "isa = PBXFileReference" in project
assert "INFOPLIST_FILE" in project

print("native quality checks: OK")
