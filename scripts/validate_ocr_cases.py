from pathlib import Path

swift = (Path(__file__).resolve().parents[1] / "native-package/TravelGuard/ScannerView.swift").read_text()

required_fragments = [
    "static func normalizeNumber",
    "itemAmounts",
    "let isTotal",
    "let isSubtotal",
    "let isTax",
    "let isService",
    "itemAmounts.reduce(0, +)",
    "OCRSupport.currency(for: store.location.countryCode)",
    "Task.detached(priority: .userInitiated)",
    "maxWidth: CGFloat = 2200",
    "isSourceTypeAvailable(.camera)",
    r"1,3}(?:[ .\u{00A0}",
]
for fragment in required_fragments:
    assert fragment in swift, f"missing OCR safeguard: {fragment}"

for forbidden in ("else if result.subtotal == nil", "Locale.current.region", "let regex = try? NSRegularExpression(pattern: \"(?<![0-9])([0-9]{1,4}"):
    assert forbidden not in swift, f"obsolete OCR/emergency logic: {forbidden}"

print("OCR deterministic safeguards: OK")
