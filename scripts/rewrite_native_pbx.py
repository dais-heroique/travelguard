from pathlib import Path
import re

ROOT = Path('/home/ubuntu/travelguard/native-ios')
APP = ROOT / 'TravelGuard'
PROJ = ROOT / 'TravelGuard.xcodeproj'

swift_files = sorted(p.name for p in APP.glob('*.swift'))
ids = {
    'project': 'A00000000000000000000001',
    'target': 'A00000000000000000000002',
    'sources': 'A00000000000000000000003',
    'frameworks': 'A00000000000000000000005',
    'resources': 'A00000000000000000000004',
    'products': 'A00000000000000000000006',
    'appref': 'A00000000000000000000007',
    'main': 'A00000000000000000000008',
    'group': 'A00000000000000000000009',
    'projDebug': 'A00000000000000000000010',
    'projRelease': 'A00000000000000000000011',
    'targetDebug': 'A00000000000000000000012',
    'targetRelease': 'A00000000000000000000013',
    'projConfigs': 'A00000000000000000000014',
    'targetConfigs': 'A00000000000000000000015',
    'assetRef': 'A00000000000000000000016',
    'assetBuild': 'A00000000000000000000017',
    'plistRef': 'A00000000000000000000018',
}
for index, name in enumerate(swift_files, 20):
    ids[name] = f'A000000000000000000000{index:02d}'
    ids[name + '_build'] = f'A000000000000000000001{index:02d}'


def list_lines(items, indent='\t\t\t'):
    return '\n'.join(f'{indent}{item},' for item in items)

build_files = [f'{ids[name + "_build"]} /* {name} in Sources */' for name in swift_files]
source_refs = [f'{ids[name]} /* {name} */' for name in swift_files]
file_objects = '\n'.join(
    f'\t\t{ids[name + "_build"]} /* {name} in Sources */ = {{ isa = PBXBuildFile; fileRef = {ids[name]} /* {name} */; }};'
    for name in swift_files
)
ref_objects = '\n'.join(
    f'\t\t{ids[name]} /* {name} */ = {{ isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {name}; sourceTree = "<group>"; }};'
    for name in swift_files
)

pbx = f'''// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{
\t}};
\tobjectVersion = 56;
\tobjects = {{

/* Begin PBXBuildFile section */
{file_objects}
\t\t{ids['assetBuild']} /* Assets.xcassets in Resources */ = {{ isa = PBXBuildFile; fileRef = {ids['assetRef']} /* Assets.xcassets */; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
{ref_objects}
\t\t{ids['assetRef']} /* Assets.xcassets */ = {{ isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
\t\t{ids['plistRef']} /* Info.plist */ = {{ isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{ids['appref']} /* TravelGuard.app */ = {{ isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = TravelGuard.app; sourceTree = BUILT_PRODUCTS_DIR; }};
/* End PBXFileReference section */

/* Begin PBXFrameworksBuildPhase section */
\t\t{ids['frameworks']} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXGroup section */
\t\t{ids['products']} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids['appref']} /* TravelGuard.app */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids['group']} /* TravelGuard */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
{list_lines(source_refs)}
\t\t\t\t{ids['assetRef']} /* Assets.xcassets */,
\t\t\t\t{ids['plistRef']} /* Info.plist */,
\t\t\t);
\t\t\tpath = TravelGuard;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{ids['main']} /* Main group */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{ids['group']} /* TravelGuard */,
\t\t\t\t{ids['products']} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
\t\t{ids['target']} /* TravelGuard */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {ids['targetConfigs']} /* Build configuration list for PBXNativeTarget "TravelGuard" */;
\t\t\tbuildPhases = (
\t\t\t\t{ids['sources']} /* Sources */,
\t\t\t\t{ids['frameworks']} /* Frameworks */,
\t\t\t\t{ids['resources']} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = TravelGuard;
\t\t\tproductName = TravelGuard;
\t\t\tproductReference = {ids['appref']} /* TravelGuard.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
\t\t{ids['project']} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tLastUpgradeCheck = 1600;
\t\t\t\tORGANIZATIONNAME = TravelGuard;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{ids['target']} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 16.0;
\t\t\t\t\t}};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {ids['projConfigs']} /* Build configuration list for PBXProject "TravelGuard" */;
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = en;
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\ten,
\t\t\t\tfr,
\t\t\t\tBase,
\t\t\t);
\t\t\tmainGroup = {ids['main']} /* Main group */;
\t\t\tproductRefGroup = {ids['products']} /* Products */;
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = (
\t\t\t\t{ids['target']} /* TravelGuard */,
\t\t\t);
\t\t}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
\t\t{ids['resources']} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{ids['assetBuild']} /* Assets.xcassets in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{ids['sources']} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{list_lines(build_files)}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
\t\t{ids['projDebug']} /* Debug */ = {{ isa = XCBuildConfiguration; buildSettings = {{ ALWAYS_SEARCH_USER_PATHS = NO; }}; name = Debug; }};
\t\t{ids['projRelease']} /* Release */ = {{ isa = XCBuildConfiguration; buildSettings = {{ ALWAYS_SEARCH_USER_PATHS = NO; }}; name = Release; }};
\t\t{ids['targetDebug']} /* Debug */ = {{ isa = XCBuildConfiguration; buildSettings = {{ ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; INFOPLIST_FILE = TravelGuard/Info.plist; IPHONEOS_DEPLOYMENT_TARGET = 17.0; PRODUCT_BUNDLE_IDENTIFIER = com.travelguard.app; PRODUCT_NAME = TravelGuard; SDKROOT = iphoneos; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = 1; }}; name = Debug; }};
\t\t{ids['targetRelease']} /* Release */ = {{ isa = XCBuildConfiguration; buildSettings = {{ ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; INFOPLIST_FILE = TravelGuard/Info.plist; IPHONEOS_DEPLOYMENT_TARGET = 17.0; PRODUCT_BUNDLE_IDENTIFIER = com.travelguard.app; PRODUCT_NAME = TravelGuard; SDKROOT = iphoneos; SWIFT_OPTIMIZATION_LEVEL = "-O"; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = 1; }}; name = Release; }};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{ids['projConfigs']} /* Build configuration list for PBXProject "TravelGuard" */ = {{ isa = XCConfigurationList; buildConfigurations = ({ids['projDebug']} /* Debug */, {ids['projRelease']} /* Release */); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
\t\t{ids['targetConfigs']} /* Build configuration list for PBXNativeTarget "TravelGuard" */ = {{ isa = XCConfigurationList; buildConfigurations = ({ids['targetDebug']} /* Debug */, {ids['targetRelease']} /* Release */); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
/* End XCConfigurationList section */
\t}};
\trootObject = {ids['project']} /* Project object */;
}}
'''
pbx = re.sub(r',([\t ]*\n[\t ]*)\);', r'\1);', pbx)
(PROJ / 'project.pbxproj').write_text(pbx)
(PROJ / 'project.xcworkspace' / 'contents.xcworkspacedata').write_text('<?xml version="1.0" encoding="UTF-8"?><Workspace version="1.0"><FileRef location="self:"></FileRef></Workspace>')
print('rewrote', PROJ)
