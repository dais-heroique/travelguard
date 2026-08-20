# TravelGuard iOS

> **Projet principal :** `native-package/TravelGuard.xcodeproj`

TravelGuard est une application iOS native SwiftUI destinée aux voyageurs : carte MapKit des signaux locaux, scanner OCR Vision, références de prix, mode hors ligne et sécurité/SOS.

## Ouvrir le projet iOS

Sur macOS avec Xcode :

```bash
git clone https://github.com/dais-heroique/travelguard.git
cd travelguard
open native-package/TravelGuard.xcodeproj
```

Dans Xcode, sélectionnez votre Team, votre iPhone et le schéma **TravelGuard** en configuration Release. Le projet natif ne dépend ni de Metro, ni de Node, ni de CocoaPods à l’exécution.

## Ce qui est inclus

Le projet natif conserve localement l’onboarding, la localisation continue avec précision, la carte MapKit avec zoom par pincement et contrôles, l’OCR Vision multilingue avec lecture structurée des montants, les alertes de régions iOS, les références locales hors ligne et le mode SOS.

TravelGuard n’affiche pas de risques géolocalisés ni de tarifs comme s’ils étaient officiels lorsqu’aucune source autorisée n’est disponible. Les références générales sont signalées comme telles et les liens vers les sources institutionnelles sont accessibles depuis l’écran Sécurité. Consultez `AUDIT_RESOLUTION.md` pour les corrections effectuées et les limites connues.

## Vérifications automatisées

Depuis la racine du dépôt, les contrôles reproductibles peuvent être lancés ainsi :

```bash
python3 -m py_compile scripts/*.py
python3 scripts/generate_native_ios.py
python3 scripts/rewrite_native_pbx.py
python3 scripts/validate_xcode_project.py
python3 scripts/validate_native_quality.py
unzip -tq TravelGuard-Xcode-FIXED.zip
```

Ces contrôles vérifient la structure PBX, les permissions, le Bundle ID, les règles anti-données fictives, l’OCR structuré, le filtrage GPS et l’intégrité de l’archive. La compilation et le test tactile final restent à exécuter sur macOS avec Xcode et un iPhone, comme décrit dans `NATIVE_TEST_MATRIX.md`.

## Dossiers à ne pas utiliser pour tester l’app native

Les dossiers `app/`, `components/`, `hooks/` et les autres fichiers Expo/Web sont conservés pour l’historique du prototype. Ils ne sont pas le chemin de lancement recommandé. Pour l’iPhone, utilisez exclusivement `native-package/TravelGuard.xcodeproj`.
