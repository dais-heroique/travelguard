# Audit TravelGuard

## Vérifications passées

La validation TypeScript, ESLint, la configuration Expo publique et l’export du bundle iOS passent. Expo Doctor passe désormais ses 18 contrôles après l’ajout d’`expo-asset`, l’alignement des modules Expo SDK 54, l’ajout des plugins dynamiques nécessaires et l’exclusion documentée des deux paquets React Navigation gérés indirectement par Expo Router.

Le bundle web ne force plus l’import de `react-native-maps` grâce à la séparation correcte entre `native-risk-map.native.tsx` et `native-risk-map.web.tsx`. L’export web et l’export iOS ont été générés avec succès. Le bundle iOS autonome produit un fichier JavaScript embarquable ; une build Release ne doit donc pas appeler Metro.

## Corrections appliquées

L’onboarding persiste maintenant son état avec AsyncStorage et le fichier importe explicitement cette dépendance. La permission de localisation est demandée à la dernière étape avec gestion des services désactivés, du refus et de l’ouverture des réglages. La permission caméra est déclarée dans la configuration iOS. Le réseau local reste déclaré uniquement pour le mode Debug Metro.

## Limites à connaître avant publication

Le scanner ouvre bien la caméra, prend une photo et affiche un résultat local de démonstration. Il ne réalise pas encore une extraction OCR réelle ni une comparaison automatique de chaque ligne avec une base officielle. Les données de la carte et du juste prix sont locales et de démonstration ; elles fonctionnent hors ligne mais ne remplacent pas encore des données officielles actualisées par ville.

Les alertes géolocalisées sont préparées pour la permission pendant l’utilisation, mais une surveillance en arrière-plan et des notifications géofencées nécessitent une implémentation native supplémentaire et un test sur appareil réel. La version Release doit être testée en mode avion après installation pour confirmer les parcours locaux.

## Procédure de validation Mac

Depuis la racine du projet, exécuter `pnpm install`, `pnpm ios:prebuild`, puis `cd ios && pod install && cd ..`. Pour tester sans Metro, exécuter `pnpm ios:release`. Pour TestFlight, ouvrir `ios/TravelGuard.xcworkspace`, sélectionner un appareil générique iOS, régler la signature Apple, puis choisir **Product → Archive**.
