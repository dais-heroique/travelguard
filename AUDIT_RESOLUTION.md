# Revue de l’audit TravelGuard

## Corrections implémentées dans le livrable natif

Le livrable canonique est désormais `native-package/TravelGuard.xcodeproj`. Les coordonnées des risques ne sont plus déplacées artificiellement autour de l’utilisateur : les risques sont filtrés par distance géographique calculée avec Core Location, puis triés par proximité. Lorsque la position n’est pas disponible, TravelGuard n’affiche plus de fausses alertes locales et demande explicitement l’autorisation.

Le service de localisation demande l’autorisation, suit la position avec `startUpdatingLocation()`, vérifie les services GPS, conserve la précision horizontale et stocke un cache horodaté invalidé après 24 heures. L’écran d’accueil distingue maintenant une protection active d’une localisation nécessaire, et la carte affiche l’état GPS, la précision, le bouton de permission et le bouton de recentrage.

Le scanner natif utilise Vision OCR sur l’image réellement capturée ou sélectionnée. Il affiche un état d’erreur lorsqu’une image ne peut pas être chargée, colore en rouge les lignes contenant des indicateurs à vérifier et reflète l’état réel du réseau au lieu d’afficher « Hors ligne » en permanence.

Les alertes de proximité utilisent désormais la surveillance de régions iOS et des notifications locales après accord de l’utilisateur. Les risques embarqués sont explicitement marqués comme **données locales de démonstration**, avec source, date et nombre de signalements. Le numéro d’urgence est choisi selon la région du téléphone au lieu d’utiliser systématiquement 112.

Le Bundle ID natif stable est `com.daisheroique.travelguard`, le scheme de deep-link est `travelguard`, et le logo de la configuration Expo restante pointe vers `assets/images/icon.png`. Les copies Xcode concurrentes ont été supprimées : le dépôt ne conserve qu’un projet canonique dans `native-package` et un ZIP de ce même dossier.

## Limites honnêtement conservées

Les risques et références de prix ne proviennent pas encore d’une base officielle par ville. Ils sont donc filtrés et présentés comme démonstration locale, mais ne doivent pas être utilisés comme vérité tarifaire ou avis de sécurité réel. Une publication sérieuse nécessite une source vérifiable, une politique de modération, des dates de validité et un mécanisme de mise à jour signé.

Le compilateur Xcode et MapKit ne sont pas disponibles dans le sandbox Linux. La validation effectuée ici couvre la structure PBX, les références `isa`, l’Info.plist, le Bundle ID, le scheme Release, l’équilibre des fichiers Swift générés et l’absence de plusieurs anti-patterns connus. La compilation finale et les gestes sur iPhone doivent être exécutés dans Xcode sur macOS.

La partie Expo/Web historique reste dans le dépôt pour conserver l’historique du développement, mais elle n’est pas le livrable recommandé et ne doit pas être ouverte pour tester l’application native. Le chemin de référence est uniquement `native-package/TravelGuard.xcodeproj`.
