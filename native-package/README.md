# TravelGuard iOS

TravelGuard est une application iOS native SwiftUI. Le projet canonique est `native-package/TravelGuard.xcodeproj` et ne dépend ni d’Expo, ni de Metro, ni de Node, ni de CocoaPods à l’exécution.

## Ouvrir sur Mac

```bash
git clone https://github.com/dais-heroique/travelguard.git
cd travelguard
open native-package/TravelGuard.xcodeproj
```

Dans Xcode, sélectionnez votre Team, votre iPhone et le schéma `TravelGuard` en configuration Release. La compilation et le test appareil final doivent être exécutés sur macOS avec Xcode.

## Fonctionnalités natives

Le paquet comprend l’onboarding, la demande de localisation, le suivi GPS avec filtrage de précision, MapKit avec zoom tactile, le scanner Vision OCR depuis caméra ou Photos, l’extraction structurée des montants, le mode hors ligne, les phrases SOS et la persistance locale.

Aucun risque géolocalisé ni tarif n’est affiché comme officiel sans source autorisée et traçable. Lorsque les sources ne sont pas disponibles, l’interface affiche explicitement l’absence de données et propose des liens institutionnels généraux. Les alertes en arrière-plan nécessitent une source de risque fiable, l’autorisation iOS `Toujours` et les notifications ; elles restent désactivées tant qu’aucune donnée sourcée n’est intégrée.

## Vérifications reproductibles

```bash
python3 -m py_compile scripts/*.py
python3 scripts/generate_native_ios.py
python3 scripts/rewrite_native_pbx.py
python3 scripts/validate_xcode_project.py
python3 scripts/validate_native_quality.py
unzip -tq TravelGuard-Xcode-FIXED.zip
```

Voir `NATIVE_TEST_MATRIX.md` pour la matrice Mac/iPhone. Les dossiers Expo/Web sont historiques ; pour l’application iPhone, utilisez exclusivement `native-package/TravelGuard.xcodeproj`.
