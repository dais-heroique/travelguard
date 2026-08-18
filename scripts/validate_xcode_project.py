from pathlib import Path
import re

roots = [Path('/home/ubuntu/travelguard/native-ios'), Path('/home/ubuntu/travelguard/native-package'), Path('/home/ubuntu/travelguard/TravelGuard-iOS')]
for root in roots:
    pbx = root / 'TravelGuard.xcodeproj' / 'project.pbxproj'
    text = pbx.read_text()
    assert text.startswith('// !$*UTF8*$!'), f'{pbx}: missing PBX header'
    assert ', ,' not in text and ',\n,' not in text, f'{pbx}: duplicate separator'
    assert not re.search(r',\s*\);', text), f'{pbx}: trailing list separator'
    assert text.count('{') == text.count('}'), f'{pbx}: unbalanced braces'
    assert text.count('(') == text.count(')'), f'{pbx}: unbalanced parentheses'
    assert 'rootObject = A00000000000000000000001' in text, f'{pbx}: missing root object'
    assert 'A00000000000000000000002 /* TravelGuard */' in text, f'{pbx}: missing target'
    assert 'A00000000000000000000007 /* TravelGuard.app */ = { isa = PBXFileReference;' in text, f'{pbx}: app reference missing isa'
    for marker in ('PBXBuildFile', 'PBXFileReference', 'PBXGroup', 'PBXNativeTarget', 'PBXProject', 'PBXResourcesBuildPhase', 'PBXSourcesBuildPhase', 'XCBuildConfiguration', 'XCConfigurationList'):
        assert marker in text, f'{pbx}: missing {marker}'
    assert (root / 'TravelGuard' / 'TravelGuardApp.swift').exists(), f'{root}: missing source'
    assert (root / 'TravelGuard' / 'Assets.xcassets' / 'AppIcon.appiconset' / 'Icon-1024.png').exists(), f'{root}: missing icon'
    scheme = root / 'TravelGuard.xcodeproj' / 'xcshareddata' / 'xcschemes' / 'TravelGuard.xcscheme'
    scheme_text = scheme.read_text()
    assert 'buildConfiguration="Release"' in scheme_text, f'{scheme}: not Release default'
    print(f'OK {root}')
