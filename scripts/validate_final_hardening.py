from pathlib import Path

source = Path(__file__).parents[1] / "native-package" / "TravelGuard" / "Models.swift"
text = source.read_text()

required = [
    'endpoint.scheme?.lowercased() == "https"',
    'host == allowedHost',
    '!host.hasPrefix("169.254.")',
    'host != "::1"',
    '!host.hasPrefix("fc")',
    '!host.hasPrefix("fd")',
    'let updatedAt: Date?',
    'feed.risks.allSatisfy',
    'data.count <= maxResponseBytes',
    'Content-Type',
    'If-None-Match',
]

missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("missing final hardening markers: " + ", ".join(missing))

print("final hardening checks: OK")
