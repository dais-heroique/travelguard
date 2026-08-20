from pathlib import Path

root = Path(__file__).resolve().parents[1]
scanner = (root / "app/(tabs)/scanner.tsx").read_text(encoding="utf-8")
map_screen = (root / "app/(tabs)/map.tsx").read_text(encoding="utf-8")
safety = (root / "app/(tabs)/safety.tsx").read_text(encoding="utf-8")
data = (root / "lib/travelguard-data.ts").read_text(encoding="utf-8")
native = (root / "native-package/TravelGuard").read_text(encoding="utf-8") if (root / "native-package/TravelGuard").is_file() else "\n".join(p.read_text(encoding="utf-8") for p in (root / "native-package/TravelGuard").glob("*.swift"))

assert "setTimeout" not in scanner
assert "takePictureAsync" in scanner
assert "photoUri" in scanner
assert "Photo capturée" in scanner
assert "Prix cohérent détecté" not in scanner
assert "tarif officiel local" not in scanner
assert "riskPlaces: RiskPlace[] = []" in data
assert "fairPrices: FairPriceItem[] = []" in data
assert "Carte native canonique" in map_screen
assert "Alertes non disponibles dans l’aperçu Expo." in safety
assert "protectionStatusLabel" in native
assert "OCRAssessment" in native
assert "MKMapRect" in native
assert "riskCacheURL" in native
assert "sourceSignal" in native
print("audit 25 deterministic checks: OK")
