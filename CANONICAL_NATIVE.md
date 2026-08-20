# TravelGuard — architecture canonique

## Application livrée

L’application iOS de production est le projet SwiftUI situé dans `native-package/TravelGuard.xcodeproj`. Il doit être ouvert directement dans Xcode, puis exécuté sur un iPhone avec une équipe de signature sélectionnée. Les fonctions de carte, localisation, géofencing, OCR, SOS, cache et références sont implémentées dans ce paquet natif.

## Branche Expo

Les dossiers `app/`, `components/` et les dépendances Expo sont conservés uniquement comme ancien prototype et aperçu de développement. Ils ne constituent pas une seconde application de production. Ils n’exposent plus de risques, distances, tarifs ou alertes statiques comme des données réelles. Les écrans Expo affichent explicitement leur statut non canonique et ne fabriquent aucun résultat scanner.

## Règle de source de vérité

> Aucun écran ne doit présenter une donnée de risque, une distance, un tarif ou une alerte comme réel sans provenance et fraîcheur connues.

Dans l’application livrée, `TravelGuardStore.risks` est la source partagée entre l’accueil, la carte, les détails, le scanner contextuel et la sécurité. Les risques provenant du cache local sont affichés avec leur âge et ne sont pas traités comme une preuve serveur intacte. Les données de démonstration statiques ne sont pas utilisées pour la production.

## Validation honnête

Les contrôles Python vérifient la structure Xcode, les permissions, l’absence de collections de démonstration, le cache versionné, le parsing OCR, les états GPS et les invariants de l’audit 25. La compilation et le test tactile sur iPhone restent des validations à exécuter dans Xcode sur macOS.
