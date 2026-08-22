from pathlib import Path
import re
from collections import Counter

path = Path(__file__).resolve().parents[1] / 'native-package' / 'TravelGuard.xcodeproj' / 'project.pbxproj'
text = path.read_text()
object_ids = re.findall(r'^\s*([A-F0-9]+)\s*/\*', text, re.MULTILINE)
references = re.findall(r'\b([A-F0-9]{20,})\b', text)
counts = Counter(object_ids)
print('path=', path)
print('balanced=', text.count('{') == text.count('}') and text.count('(') == text.count(')'))
print('duplicate_definitions=', [(key, value) for key, value in counts.items() if value > 1])
print('undefined_references=', sorted(set(references) - set(object_ids)))
print('conflict_markers=', any(marker in text for marker in ('<<<<<<<', '=======', '>>>>>>>')))
print('absolute_home_path=', '/home/ubuntu' in text)
print('utf8_header=', text.startswith('// !$*UTF8*$!'))
