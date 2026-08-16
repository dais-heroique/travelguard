# Ouvrir TravelGuard dans Xcode

Le projet natif iOS se trouve dans `ios/TravelGuard.xcodeproj`. Après installation de CocoaPods, le workspace recommandé sera `ios/TravelGuard.xcworkspace`.

## Ouverture rapide

Sur macOS, double-cliquez sur `TravelGuard-Xcode.command` à la racine du projet. Le script ouvre automatiquement `TravelGuard.xcworkspace` lorsqu’il existe, sinon `TravelGuard.xcodeproj`.

Si macOS bloque le script au premier lancement, faites un clic droit sur le fichier, choisissez **Ouvrir**, puis confirmez. Vous pouvez aussi l’exécuter depuis Terminal avec `bash TravelGuard-Xcode.command`.

## Première installation sur Mac

Depuis Terminal, placez-vous à la racine du projet, installez les dépendances JavaScript, puis installez les pods iOS :

```bash
pnpm install
cd ios
pod install
cd ..
```

Après `pod install`, ouvrez de préférence `ios/TravelGuard.xcworkspace`, et non le fichier `.xcodeproj` seul.

## Réglages Xcode à vérifier

Dans Xcode, sélectionnez la cible **TravelGuard**, choisissez une équipe Apple dans **Signing & Capabilities**, puis vérifiez que le bundle identifier correspond à celui déclaré dans App Store Connect. Les messages de confidentialité caméra et localisation sont déjà configurés dans `Info.plist`.

Le lancement avec une vraie caméra et la localisation doit être testé sur un iPhone réel. Le simulateur Xcode ne reproduit pas entièrement les permissions et les capteurs d’un appareil.

## Archive et publication

Choisissez un appareil générique iOS, puis **Product → Archive**. Dans l’Organizer, vérifiez les warnings, validez l’archive et envoyez-la à App Store Connect. La signature, l’équipe Apple, les certificats, les profils de provisioning et les informations App Store Connect doivent être configurés sur le Mac du propriétaire du compte Apple Developer.

Le projet reste basé sur Expo et peut aussi être construit avec les profils définis dans `eas.json` (`development`, `preview`, `production`).
