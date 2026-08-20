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

Les risques et références de prix actuellement embarqués sont des **données locales de démonstration**. Ils ne constituent pas une source officielle de sécurité ou de tarification. Consultez `AUDIT_RESOLUTION.md` pour les corrections effectuées et les limites connues.

## Dossiers à ne pas utiliser pour tester l’app native

Les dossiers `app/`, `components/`, `hooks/` et les autres fichiers Expo/Web sont conservés pour l’historique du prototype. Ils ne sont pas le chemin de lancement recommandé. Pour l’iPhone, utilisez exclusivement `native-package/TravelGuard.xcodeproj`.
