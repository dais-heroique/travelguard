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

## Contrat du feed de risques

Le paquet natif tente au démarrage l’URL `RiskFeedURL` déclarée dans l’Info.plist. Cette valeur est volontairement vide par défaut : aucune API mondiale fiable et universelle n’est présumée. Lorsqu’un opérateur configure une source autorisée, elle doit renvoyer un JSON de la forme suivante : `{"schemaVersion":1,"fetchedAt":"2026-08-20T12:00:00Z","risks":[...]}`. Chaque risque doit inclure une source, un `sourceType` structuré, une date récente, des coordonnées valides, un score borné, un rayon d’alerte et, si disponible, des preuves identifiables et dédupliquées.

Une source de pays ou d’avis général ne doit pas être convertie automatiquement en risque ponctuel de géofencing : cela créerait une fausse précision géographique. Les données non validées, expirées, révoquées, futures au-delà de la tolérance d’horloge ou dépassant les limites de cache sont rejetées.

La version actuelle fonctionne donc correctement hors ligne et sans données inventées, mais l’état « Protection active » ne peut apparaître qu’après fourniture d’un feed autorisé et test de ses notifications sur appareil réel.
