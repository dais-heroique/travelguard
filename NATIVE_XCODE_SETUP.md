# Ouvrir TravelGuard dans Xcode

Cette version est native SwiftUI et ne nécessite ni Node, ni Metro, ni CocoaPods pour fonctionner sur l’iPhone après installation.

## Méthode recommandée depuis GitHub

Fermer les anciennes copies de TravelGuard, puis ouvrir Terminal et exécuter exactement :

```bash
cd ~/Downloads
rm -rf travelguard-native
mkdir travelguard-native
cd travelguard-native
git clone https://github.com/dais-heroique/travelguard.git repo
cd repo
find . -name "TravelGuard.xcodeproj" -print
```

La commande `find` affiche les emplacements disponibles. Pour ouvrir automatiquement le paquet natif corrigé, exécuter ensuite :

```bash
PROJECT=$(find "$PWD/TravelGuard-Xcode-FIXED" -maxdepth 1 -name "TravelGuard.xcodeproj" -print -quit)
if [ -z "$PROJECT" ]; then
  PROJECT=$(find "$PWD" -path "*/TravelGuard-Xcode-FIXED/TravelGuard.xcodeproj" -print -quit)
fi
if [ -z "$PROJECT" ]; then
  echo "Projet Xcode introuvable"
  exit 1
fi
printf 'Ouverture de : %s\n' "$PROJECT"
open "$PROJECT"
```

## Si le dépôt est déjà téléchargé

Depuis n’importe quel dossier contenant la copie du dépôt :

```bash
cd ~/Downloads/travelguard
PROJECT=$(find . -path "*/TravelGuard-Xcode-FIXED/TravelGuard.xcodeproj" -print -quit)
[ -n "$PROJECT" ] || PROJECT=$(find . -path "*/native-package/TravelGuard.xcodeproj" -print -quit)
[ -n "$PROJECT" ] || { echo "TravelGuard.xcodeproj introuvable"; exit 1; }
printf 'Ouverture de : %s\n' "$PROJECT"
open "$PROJECT"
```

Dans Xcode, sélectionner ensuite la cible **TravelGuard**, choisir son **Team**, sélectionner l’iPhone connecté et lancer avec **Run**. Pour éviter Metro, utiliser le schéma partagé configuré en **Release**.

La compilation et la signature doivent être réalisées sur macOS avec Xcode. Le runtime natif ne dépend pas d’un Mac allumé après installation sur l’iPhone.
