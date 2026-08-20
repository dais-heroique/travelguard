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

## Corrections supplémentaires de Pasted_content_08.txt

La carte ne recentre plus la région à chaque mise à jour GPS : elle effectue un centrage initial unique, puis seulement sur une action explicite de l’utilisateur. Les boutons de zoom sont compacts et la liaison plein écran conserve la région courante sans recentrage déclenché par le GPS.

Le scanner normalise l’orientation de l’image, augmente légèrement le contraste, utilise les langues Vision disponibles parmi le français, l’anglais, l’italien, l’espagnol, l’allemand, le portugais, le slovène et le croate, réinitialise la sélection PhotosPicker après analyse et extrait les montants avec devise, sous-total, taxes, service et total lorsqu’ils sont lisibles. Cette lecture reste une aide locale : elle ne remplace pas une expertise comptable et ne peut pas déduire un prix juste sans référence officielle par ville.

Le service GPS rejette les positions dont la précision dépasse 100 mètres pour le calcul des risques, réduit la fréquence de mise à jour et limite le reverse geocoding aux déplacements d’au moins 2 kilomètres. Les erreurs de géocodage sont désormais visibles. Les alertes de proximité ne demandent plus la permission Notifications au démarrage : l’utilisateur les active explicitement, le choix est persisté, la permission est affichée séparément et les régions utilisent un rayon prudent de 250 mètres.

Les dates des données locales sont fixes plutôt que recalculées à chaque lancement. Un score de confiance dérivé combine la gravité initiale, la fraîcheur, le nombre de signalements et un signal de fiabilité de source ; les données de démonstration restent toutefois clairement étiquetées. Le README racine place `native-package/TravelGuard.xcodeproj` en première position afin d’éviter le lancement involontaire de l’ancien prototype Expo.

## Corrections supplémentaires de Pasted_content_09.txt

Les risques et distances ne sont plus affichés comme fiables lorsque la précision GPS dépasse 100 mètres. L’interface distingue désormais une position imprécise, l’absence de position et l’absence de données connues dans le rayon local. Les distances sont formatées en mètres sous un kilomètre puis en kilomètres au-delà. Le score est présenté comme un **indice indicatif**, et non comme une mesure scientifique indépendante.

Après un refus définitif de la localisation, le bouton ouvre les Réglages iOS avec une indication « Réglages → TravelGuard → Localisation ». La détection OCR conserve les langues de voyage et la lecture structurée ; les faux positifs liés à des mots comme « Tourist information » sont réduits en exigeant un montant sur la ligne suspecte.

Le remplacement de `sampleRisks` et `samplePrices` par une base officielle distante n’est pas effectué automatiquement : aucune source, API, contrat de données ou clé de service n’a été fournie. Les données embarquées restent donc explicitement démonstratives et ne doivent pas être présentées comme des informations officielles ou exhaustives.
