# TravelGuard natif — ouverture Xcode

Le dépôt contient un seul projet iOS canonique : `native-package/TravelGuard.xcodeproj`. Le dossier `native-package/TravelGuard/` contient les sources SwiftUI, les permissions et les ressources. Le ZIP `TravelGuard-Xcode-FIXED.zip` est seulement une copie de téléchargement de ce même dossier.

Depuis le Mac, exécutez :

```bash
cd ~/Downloads
rm -rf travelguard-native
git clone https://github.com/dais-heroique/travelguard.git travelguard-native
cd travelguard-native
open ./native-package/TravelGuard.xcodeproj
```

Dans Xcode, sélectionnez la cible **TravelGuard**, votre **Team**, l’iPhone connecté et le schéma partagé **TravelGuard**. Le schéma utilise Release afin que l’application native n’ait besoin ni de Metro, ni de Node, ni d’un serveur Mac après installation.

Le Bundle ID fourni est `com.daisheroique.travelguard`. Remplacez-le par un identifiant enregistré dans votre compte Apple Developer si nécessaire. Faites ensuite **Product → Clean Build Folder**, puis **Run**.

Les risques et références de prix inclus sont explicitement des données locales de démonstration, avec source et date affichées. Ils ne constituent pas une base officielle synchronisée. Pour une publication réelle, il faudra brancher une source de données vérifiable par ville.

En cas d’erreur, vérifiez d’abord le chemin exact :

```bash
pwd
find . -maxdepth 3 -name "TravelGuard.xcodeproj" -print
```

Le résultat attendu est :

```text
./native-package/TravelGuard.xcodeproj
```
