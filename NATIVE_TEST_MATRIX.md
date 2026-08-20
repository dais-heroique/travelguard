# Matrice de validation native

## Contrôles automatisés dans le dépôt

| Domaine | Contrôle |
|---|---|
| Générateur | Compilation Python de `generate_native_ios.py`, `rewrite_native_pbx.py`, `validate_xcode_project.py` et `validate_native_quality.py` |
| Projet Xcode | Présence des objets PBX, `isa`, Bundle ID stable, `INFOPLIST_FILE`, cible Release et archive intacte |
| Info.plist | `CFBundleIdentifier`, exécutable, type de paquet, caméra et localisation |
| Données | Aucun écran natif ne lit `sampleRisks`; `trustedRisks` reste vide tant qu’une source géolocalisée autorisée n’est pas intégrée |
| OCR | Langues Vision filtrées selon les langues réellement supportées par iOS, extraction des montants, total calculé et écart signalé |
| GPS | Positions imprécises conservées avec état dégradé ; distances masquées seulement au-delà de 200 m |
| Permissions | Ouverture des Réglages iOS après refus définitif de localisation |
| Archive | `unzip -t` vérifie l’intégrité de `TravelGuard-Xcode-FIXED.zip` |

## Validation à exécuter sur Mac/Xcode

Le sandbox ne possède pas Xcode ni un iPhone connecté. Sur le Mac, il faut ouvrir `native-package/TravelGuard.xcodeproj`, sélectionner une Team Apple, choisir l’iPhone et lancer la cible Release. Le parcours doit être vérifié en autorisant puis refusant la localisation, en coupant le réseau, en prenant une photo d’addition, en zoomant la carte avec deux doigts et en activant/désactivant les alertes de proximité.

## Audit 13 — GPS et géofencing

| Scénario | Résultat attendu | Validation |
|---|---|---|
| Lancement avec cache GPS datant de moins de 24 h et alertes activées | Les anciennes régions sont supprimées ; aucune région n’est recréée avant une position fraîche | Appareil/Xcode |
| Autorisation de localisation nouvellement accordée | `requestLocation()` est appelé et la carte reçoit une position ponctuelle | Appareil/Xcode |
| GPS à 150 m puis 80 m | La position à 150 m est conservée avec un état approximatif, puis remplacée par la position précise | Appareil/Xcode |
| Risques synchronisés après démarrage | `TravelGuardStore.updateRisks(_:)` transmet les risques à `LocationService.updateRisks(_:)` et déclenche un recalcul après position fraîche | Test déterministe + appareil |
| Marche, véhicule, arrière-plan et écran verrouillé | Les mises à jour de position et les régions se recalculent sans régression ; vérifier les autorisations iOS Always et Background Modes | Appareil/Xcode |
| Erreur GPS `kCLErrorLocationUnknown` ou `denied` | Le code CLLocation est journalisé et un message distinct est présenté | Test appareil |

## Audit 14 — permissions, batterie et état du monitoring

| Scénario | Résultat attendu | Validation |
|---|---|---|
| Notifications acceptées avant l’autorisation Always | Les alertes restent en attente et ne sont pas désactivées ; les régions s’installent uniquement après confirmation Always puis position à ±200 m ou mieux | Appareil/Xcode |
| Notifications refusées | Le toggle revient à désactivé et aucune région n’est surveillée | Appareil/Xcode |
| Position fraîche à ±500–800 m | La carte conserve la position, mais le géofencing reste inactif et l’interface indique une précision insuffisante | Appareil/Xcode |
| Cache restauré au lancement | L’interface affiche « Dernière position connue » jusqu’au nouveau fix ; aucune alerte n’est restaurée sur le cache | Appareil/Xcode |
| App ouverte sans alertes | Aucun tracking continu ne démarre ; seules les demandes ponctuelles nécessaires sont effectuées | Instruments/Xcode |
| Déplacement inférieur à 500 m | Les régions ne sont pas recalculées à chaque mise à jour GPS ; au-delà de 500 m ou après `updateRisks`, elles le sont | Test déterministe + appareil |
| `updateRisks([])` | Le toggle et `monitoringActive` passent à désactivé et toutes les régions sont arrêtées | Test déterministe |
