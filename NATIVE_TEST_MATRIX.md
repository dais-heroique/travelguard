# Matrice de validation native

## Contrôles automatisés dans le dépôt

| Domaine | Contrôle |
|---|---|
| Générateur | Compilation Python de `generate_native_ios.py`, `rewrite_native_pbx.py`, `validate_xcode_project.py` et `validate_native_quality.py` |
| Projet Xcode | Présence des objets PBX, `isa`, Bundle ID stable, `INFOPLIST_FILE`, cible Release et archive intacte |
| Info.plist | `CFBundleIdentifier`, exécutable, type de paquet, caméra et localisation |
| Données | Aucun écran natif ne lit `sampleRisks`; `trustedRisks` reste vide tant qu’une source géolocalisée autorisée n’est pas intégrée |
| OCR | Langues Vision filtrées selon les langues réellement supportées par iOS, extraction des montants, total calculé et écart signalé |
| GPS | Positions dont la précision dépasse 100 m ignorées pour les distances et risques locaux |
| Permissions | Ouverture des Réglages iOS après refus définitif de localisation |
| Archive | `unzip -t` vérifie l’intégrité de `TravelGuard-Xcode-FIXED.zip` |

## Validation à exécuter sur Mac/Xcode

Le sandbox ne possède pas Xcode ni un iPhone connecté. Sur le Mac, il faut ouvrir `native-package/TravelGuard.xcodeproj`, sélectionner une Team Apple, choisir l’iPhone et lancer la cible Release. Le parcours doit être vérifié en autorisant puis refusant la localisation, en coupant le réseau, en prenant une photo d’addition, en zoomant la carte avec deux doigts et en activant/désactivant les alertes de proximité.
