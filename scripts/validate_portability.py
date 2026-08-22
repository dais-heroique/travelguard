from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for name in ("generate_native_ios.py", "rewrite_native_pbx.py"):
    text = (ROOT / "scripts" / name).read_text()
    assert "/home/ubuntu" not in text, f"absolute sandbox path remains in {name}"
print("portability checks: OK")
