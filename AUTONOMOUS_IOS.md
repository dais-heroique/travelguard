# TravelGuard — build iOS autonome

TravelGuard possède deux modes de lancement. Le mode **Debug** utilise Metro et nécessite que le Mac soit allumé. Le mode **Release** intègre le bundle JavaScript dans l’application iOS ; l’iPhone peut alors lancer TravelGuard sans Metro, sans serveur local et sans Mac actif.

## Build locale sur Mac

Depuis la racine du projet :

```bash
pnpm install
pnpm ios:prebuild
cd ios
pod install
cd ..
pnpm ios:release
```

La commande `ios:release` utilise `expo run:ios` en configuration Release et sur un appareil réel. Elle génère et embarque le JavaScript dans l’application. Ne lance pas `npx expo start` pour cette étape.

Pour une archive destinée à TestFlight, ouvre ensuite le workspace :

```bash
open ios/TravelGuard.xcworkspace
```

Dans Xcode, sélectionne un appareil générique iOS, vérifie **Signing & Capabilities**, puis choisis **Product → Archive**. L’archive Release ne dépend pas de l’adresse `192.168.x.x:8081`.

## Build EAS de production

Avec un compte Expo/EAS configuré :

```bash
npx eas login
npx eas build:configure
npx eas build --platform ios --profile production
```

Le profil `production` est configuré pour une distribution App Store. Une fois l’archive prête, elle peut être envoyée avec :

```bash
npx eas submit --platform ios --profile production
```

## Fonctions disponibles hors connexion

Les écrans Accueil, Carte avec les données locales incluses, Scanner et ses états locaux, SOS, phrases locales, préférences d’onboarding et références du juste prix incluses dans l’application restent accessibles sans réseau. Les données distantes, les nouvelles alertes, les mises à jour de tarifs et une éventuelle analyse OCR serveur nécessitent une connexion et doivent afficher un état indisponible plutôt qu’un écran vide.

Le mode hors ligne ne peut pas fournir de nouvelles données officielles qui n’ont jamais été téléchargées. Pour une version complète, il faudra ajouter des packs de villes téléchargeables avant le départ et une file de synchronisation différée.

## Test de validation

Après installation de la Release sur l’iPhone, active le mode avion et relance TravelGuard. Vérifie que l’onboarding terminé, la carte locale, les références du juste prix, les phrases SOS et la navigation restent utilisables. Si l’application affiche `No script URL provided`, c’est que tu as lancé une build Debug : utilise `pnpm ios:release` ou une archive Xcode Release.
