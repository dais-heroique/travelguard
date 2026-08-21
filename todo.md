# TravelGuard — TODO

- [x] Branding TravelGuard et icône d’application personnalisée
- [x] Thème iOS TravelGuard et palette de marque
- [x] Navigation principale Accueil / Carte / Scanner / Sécurité
- [x] Accueil avec statut de protection et actions rapides
- [x] Carte interactive des risques avec filtres
- [x] Fiche lieu avec score de confiance et signaux
- [x] Scanner caméra pour menu, billet et addition
- [x] Flux d’analyse OCR et états de résultat
- [x] Indice du juste prix par ville et catégorie
- [x] Mode hors ligne avec données locales et état de synchronisation
- [x] Alertes géolocalisées et réglages de permission
- [x] Mode SOS avec phrases locales et actions d’urgence
- [x] Persistance locale des préférences et lieux enregistrés
- [x] États de chargement, erreur, permission refusée et absence de réseau
- [x] Tests unitaires et vérification TypeScript/lint
- [x] Vérification visuelle des écrans et responsive web preview
- [ ] Checkpoint final livrable après publication des corrections de l’audit
- [x] Corriger la prévisualisation web après conflit d’import react-native-maps
- [x] Corriger le sizing du texte et les safe areas en bas sur iPhone
- [x] Revoir la palette TravelGuard avec contraste et confort visuel
- [x] Ajouter un onboarding approfondi au premier lancement
- [x] Persister l’état de fin d’onboarding localement
- [x] Demander la localisation avec écran pédagogique puis permission native
- [x] Gérer permission localisation refusée, limitée et ouverture des réglages
- [x] Préparer les métadonnées et permissions iOS pour Xcode/App Store
- [ ] Vérifier le rendu iOS portrait et les zones sûres après refonte
- [ ] Résoudre l’erreur SwiftCompile dans ExpoModulesProvider sur Xcode
- [ ] Déplacer Derived Data Xcode vers le disque externe Data3
- [ ] Nettoyer les anciens caches Xcode après déplacement
- [ ] Vérifier que le projet iOS complet, et pas seulement les fichiers Xcode, est présent sur Data3
- [ ] Reconfigurer les chemins persistants de Derived Data et Pods sur Data3
- [ ] Vérifier la sauvegarde et la structure du disque Data3 avant toute partition APFS
- [ ] Choisir la taille APFS adaptée au stockage Xcode et Derived Data
- [x] Ajouter la permission réseau local iOS pour le dev client Metro
- [ ] Tester le bundle JavaScript sur iPhone via le même réseau Wi-Fi
- [x] Préparer une build iOS autonome sans dépendance à Metro
- [x] Résoudre le refus de connexion iPhone vers Metro sur 192.168.1.23:8081
- [x] Intégrer le bundle JavaScript dans une build iOS autonome sans Metro
- [x] Rendre les fonctions essentielles disponibles sans connexion réseau
- [ ] Ajouter un état réseau clair et une synchronisation différée
- [x] Documenter la génération d’une archive TestFlight/App Store autonome
- [x] Auditer tous les écrans, routes, imports et dépendances
- [x] Vérifier les permissions natives et les parcours premier lancement
- [x] Vérifier la build Release sans Metro et les fonctions hors ligne
- [x] Corriger les problèmes reproductibles et documenter les limites
- [x] Corriger le positionnement vertical du contenu sur iPhone
- [x] Remplacer le statut hors ligne manuel par le vrai état réseau
- [x] Détecter et afficher la ville réelle depuis la localisation
- [x] Remplacer « Nomade digital » par « Télétravailleur itinérant »
- [ ] Tester connecté, hors ligne et localisation refusée
- [ ] Remplacer le dossier local par le dépôt GitHub dais-heroique/travelguard avec sauvegarde de l’ancien
- [ ] Réinstaller les dépendances et régénérer le projet iOS depuis le dépôt
- [ ] Ouvrir et vérifier le workspace Xcode issu du dépôt
- [x] Configurer un schéma Xcode Release autonome sans Metro
- [x] Vérifier que le bundle JavaScript est intégré à la cible iOS
- [ ] Tester le lancement en coupant le réseau et tout processus Mac
- [ ] Valider les commandes Debug Metro et Release autonome
- [ ] Publier les derniers scripts et réglages dans GitHub dais-heroique/travelguard
- [ ] Documenter les commandes Mac pour chaque mode de lancement
- [ ] Synchroniser le dossier Mac avec le commit GitHub 43a1701 et rendre ios:standalone disponible
- [x] Créer un projet iOS natif SwiftUI séparé de l’application Expo
- [x] Recréer le thème, les modèles locaux et la navigation en Swift
- [x] Recréer onboarding, localisation, carte, scanner, juste prix, hors ligne et SOS en Swift
- [x] Ajouter permissions iOS, configuration Xcode et bundle ID natif
- [ ] Compiler et tester la version native sur iPhone — requis sur macOS/Xcode
- [x] Placer TravelGuard.xcodeproj directement à la racine du paquet natif
- [x] Rendre le paquet indépendant d’Expo, Metro, Node et CocoaPods
- [ ] Vérifier le lancement après sélection Team et iPhone dans Xcode — requis sur macOS/Xcode
- [x] Auditer et améliorer les parcours SwiftUI du paquet natif
- [x] Compléter OCR, localisation, carte et hors ligne en natif
- [ ] Vérifier la compilation et le lancement Xcode sur iPhone — requis sur macOS/Xcode
- [x] Mesurer la taille des dossiers Expo, natif et assets
- [x] Créer un livrable SwiftUI séparé sans l’ancien projet Expo
- [x] Compresser ou retirer les assets natifs inutilisés
- [x] Vérifier la taille finale et les fonctions conservées

- [x] Corriger le fichier TravelGuard.xcodeproj invalide signalé par Xcode
- [x] Vérifier que le project.pbxproj réparé est parseable et que les références sources sont valides
- [x] Régénérer le ZIP natif après correction du projet Xcode

- [x] Vérifier le contenu exact de l’archive Xcode livrée et éliminer les copies ambiguës
- [x] Fournir un chemin unique et une commande Mac d’ouverture du projet corrigé

- [x] Synchroniser le projet natif SwiftUI corrigé vers GitHub
- [x] Vérifier le contenu du dépôt distant après synchronisation
- [x] Documenter les commandes Mac pour cloner, reconstruire et ouvrir le projet Xcode

- [x] Remplacer complètement la structure PBX du projet publié après parse error Xcode persistant
- [x] Vérifier le projet corrigé avec une validation PBX plus stricte avant publication

- [x] Corriger les objets PBX auxquels il manque la clé obligatoire isa
- [x] Ajouter une validation stricte des objets PBX avant toute nouvelle livraison

- [x] Corriger le bundle Release sans CFBundleIdentifier signalé par CoreDevice
- [x] Vérifier la présence de CFBundleIdentifier dans l’Info.plist embarqué avant publication

- [x] Réparer le bouton Continuer de l’onboarding natif
- [x] Afficher la position réelle de l’utilisateur sur la carte
- [x] Garantir des risques visibles par défaut sur la carte
- [x] Ouvrir la carte en plein écran au toucher

- [x] Afficher un résultat explicite lorsque l’OCR ne détecte aucun texte
- [x] Colorer en rouge les lignes ou mots identifiés comme suspects
- [x] Remplir Protection active avec statut réseau, ville, position et risques proches

- [x] Corriger l’erreur SwiftUI onChange sur CLLocationCoordinate2D non Equatable

- [x] Remplacer les points rouges de Protection active par des indicateurs de risque explicites
- [x] Corriger la carte plein écran vide et ajouter zoom, déplacement et contrôles utilisateur

- [x] Supprimer les boutons de zoom intrusifs et préserver le zoom MapKit à deux doigts
- [x] Repositionner le bouton de recentrage dans la carte plein écran
- [x] Rendre Protection active visible et informative sur iPhone

- [x] Empêcher le recentrage automatique de la carte pendant le pincement à deux doigts
- [x] Vérifier que le zoom tactile reste à la position choisie sans double-clic

- [x] Revoir l’architecture native SwiftUI et la configuration Xcode de bout en bout
- [x] Rechercher les défauts de concurrence, état, permissions et cycle de vie
- [x] Rechercher les défauts de carte, OCR, onboarding et navigation utilisateur
- [x] Valider les références PBX, Info.plist, schéma Release et archive finale

- [x] Stabiliser la taille initiale de MapKit et éviter CAMetalLayer width=0
- [x] Vérifier le cycle de présentation plein écran de la carte sur iPhone

- [x] Rendre public le dépôt GitHub dais-heroique/travelguard et vérifier sa visibilité

# Audit Pasted_content_07.txt

- [x] Corriger la carte native réelle, le zoom gestuel, le recentrage et les coordonnées géographiques ; la carte Web legacy reste hors du livrable natif
- [x] Corriger la localisation : demande de permission, suivi continu, cache horodaté et états d’erreur
- [x] Remplacer le scanner démonstratif par un flux photo/OCR local réellement relié à l’image
- [x] Corriger l’état réseau du scanner et les états de protection trompeurs
- [x] Corriger le numéro SOS international et implémenter les alertes locales par régions iOS
- [x] Corriger les distances, sources, dates et signalements ; la sélection native ouvre le détail du risque
- [x] Corriger Bundle ID, scheme, logo local et configuration iOS signalés par l’audit
- [x] Lire les lignes restantes de l’audit et associer chaque point à une validation structurelle ou une limite documentée

# Audit Pasted_content_08.txt

- [x] Empêcher le recentrage automatique de la carte après le premier centrage
- [x] Ajouter un mode de zoom explicite sans réinitialiser le geste utilisateur
- [x] Renforcer l’OCR avec extraction des montants, devise, taxes, service et total
- [x] Ajouter les langues OCR de voyage et remettre PhotosPicker à nil après analyse
- [x] Améliorer rotation, contraste et préparation d’image avant Vision OCR
- [x] Corriger les alertes : activation explicite, persistance cohérente et rayon géographique prudent
- [x] Filtrer les positions GPS imprécises et limiter le reverse geocoding
- [x] Adapter la précision GPS et le suivi pour réduire la consommation énergétique
- [x] Relire la seconde partie de l’audit et documenter les limites restantes

# Audit Pasted_content_09.txt

- [x] Masquer les distances et risques quand la précision GPS est insuffisante
- [x] Formater les distances en mètres ou kilomètres lisibles
- [x] Distinguer absence de données locales et absence de risque
- [x] Rendre le score de confiance explicitement indicatif et traçable
- [x] Ouvrir les Réglages iOS si la permission de localisation est définitivement refusée
- [x] Vérifier et conserver OCR multilingue, préparation d’image et extraction structurée
- [x] Réduire les faux positifs de détection de frais et documenter l’analyse indicative
- [x] Relire l’audit complet et associer chaque point à une validation

# Finalisation complète demandée
- [x] Identifier des sources officielles réellement utilisables pour risques et prix
- [x] Remplacer les données de démonstration par des données sourcées ou afficher un état indisponible honnête
- [x] Renforcer et tester l’OCR structuré sur menus et additions multilingues
- [x] Ajouter les validations déterministes des permissions, GPS, réseau, carte et scanner
- [ ] Valider le paquet natif final sur macOS/Xcode et iPhone lorsque possible

# Poursuite automatique
- [x] Auditer le dernier état après le checkpoint f8b363a
- [x] Ajouter les intégrations sans clé et les états hors ligne robustes
- [x] Renforcer les tests déterministes du natif
- [x] Améliorer les parcours et la robustesse UI
- [x] Régénérer, publier et sauvegarder le paquet final

# Corrections Pasted_content_10
- [x] Empêcher le premier recentrage automatique après interaction utilisateur sur la carte
- [x] Vérifier et corriger partout la prise en compte de la précision GPS
- [x] Vérifier l’absence de données de démonstration présentées comme réelles
- [x] Auditer le pipeline OCR, extraction des prix et comparaison locale
- [x] Vérifier que les alertes géolocalisées restent explicitement non-production sans source fiable
- [x] Corriger le formatage des distances en kilomètres
- [x] Distinguer absence de données et absence de risque dans tous les écrans
- [x] Régénérer, tester et publier la nouvelle archive native

# Synchronisation publique finale
- [x] Vérifier la visibilité publique et l’état de la branche principale
- [x] Synchroniser la dernière version validée vers GitHub
- [x] Contrôler le commit et les fichiers clés sur le dépôt distant

# Corrections Pasted_content_11
- [x] Réenregistrer automatiquement les régions après autorisation Always
- [x] Synchroniser l’état des notifications et annuler le toggle si refus
- [x] Limiter le géofencing aux risques proches et gérer les régions obsolètes
- [x] Corriger les montants européens et les séparateurs de milliers
- [x] Éviter de prendre le premier prix pour le sous-total
- [x] Somme des articles, taxes et service avec total attendu
- [x] Détection OCR par libellés et contexte de devise
- [x] Déduire la devise depuis le document ou la région GPS
- [x] Utiliser le pays de position pour le numéro d’urgence
- [x] Gérer l’échec d’ouverture de l’appel d’urgence
- [x] Supprimer le code mort de date locale
- [x] Déplacer Vision OCR hors du thread principal
- [x] Redimensionner les photos avant OCR
- [x] Vérifier la disponibilité de la caméra
- [x] Régénérer, valider et publier la nouvelle version

# Corrections Pasted_content_12
- [x] Séparer l’interaction utilisateur du centrage programmatique
- [x] Remplacer les gestes SwiftUI concurrents par une détection caméra MapKit adaptée
- [x] Déplacer les contrôles de zoom dans l’overlay de la carte
- [x] Ajouter un recentrage cohérent en plein écran
- [x] Afficher les risques même avec GPS approximatif et dégrader seulement les distances
- [x] Remplacer le seuil GPS unique par précis, approximatif et imprécis
- [x] Supprimer le centrage visuel par défaut sur Paris sans position
- [x] Afficher une ville et un état de localisation explicites
- [x] Séparer localisation, chargement, absence de risque, erreur et base vide
- [x] Préparer un calcul de distances en une seule passe
- [x] Limiter le zoom maximal à un rayon local utile
- [x] Régénérer, valider et publier la version corrigée

# Corrections Pasted_content_13
- [x] Exiger une position fraîche avant de restaurer le géofencing
- [x] Relancer une position ponctuelle après autorisation
- [x] Conserver les positions GPS imprécises avec un état dégradé
- [x] Ne jamais utiliser le cache ancien pour activer des alertes
- [x] Journaliser les erreurs CLLocation avec leur code
- [x] Ajouter une méthode publique de rafraîchissement des régions
- [x] Recalculer les régions après synchronisation des risques
- [x] Classer les risques par proximité, gravité, confiance et récence
- [x] Documenter et tester marche, véhicule, arrière-plan et écran verrouillé
- [x] Régénérer, valider et publier la version corrigée

# Synchronisation main publique
- [x] Vérifier que le dépôt GitHub est public
- [x] Vérifier l’écart entre la branche locale et main distant
- [x] Pousser la dernière version sur main
- [x] Confirmer le commit et les fichiers clés sur GitHub

# Corrections Pasted_content_14
- [x] Éliminer la race condition entre autorisation Always et notifications
- [x] Réactiver le monitoring lorsque Always est effectivement accordé
- [x] Désactiver l’état d’alerte lorsque updateRisks reçoit une liste vide
- [x] Interdire le géofencing avec une précision GPS supérieure à 200 m
- [x] Réduire le tracking GPS permanent et réactiver les mises à jour seulement au besoin
- [x] Réduire les recalculs de régions aux déplacements significatifs ou synchronisations
- [x] Remplacer le score de tri par une formule normalisée et documentée
- [x] Libérer NetworkMonitor avec deinit
- [x] Afficher explicitement dernière position connue versus position actuelle
- [x] Régénérer, valider et publier la version corrigée

# Vérification Pasted_content_15
- [x] Comparer chaque point à la version native actuelle
- [x] Corriger tout écart résiduel réellement présent
- [x] Régénérer, valider et publier si nécessaire

# Corrections Pasted_content_21
- [x] Désactiver les alertes après refus de l’autorisation Always
- [x] Désactiver les alertes si les notifications sont refusées dans Réglages
- [x] Arrêter les anciennes régions lorsque la précision GPS dépasse 200 m
- [x] Afficher un bouton adapté à permission absente versus GPS imprécis
- [x] Ne pas recentrer sur une position issue du cache
- [x] Exposer une source de risques partagée entre carte et géofencing
- [x] Utiliser les risques synchronisés pour activer le toggle
- [x] Mettre monitoringActive à false avant chaque nouvelle synchronisation
- [x] Supprimer le flag waitingForAlwaysAuthorization devenu inutile
- [x] Régénérer, valider et publier la version corrigée

# Corrections Pasted_content_22
- [x] Persister les risques synchronisés pour le mode hors ligne
- [x] Valider strictement les risques entrants
- [x] Protéger les synchronisations contre les réponses obsolètes
- [x] Ajouter une chaîne repository locale/offline documentée
- [x] Afficher les risques selon le viewport de la carte
- [x] Connecter le plein écran à la source de risques du store
- [x] Ajouter un état de recherche de position et l’âge du cache
- [x] Passer les contrôles carte à 44x44 et compléter VoiceOver
- [x] Séparer visuellement risque et confiance
- [x] Contextualiser et dédupliquer les notifications
- [x] Améliorer le statut ville/pays et les erreurs GPS séparées
- [x] Régénérer, valider et publier la version corrigée

# Corrections Pasted_content_23
- [x] Remplacer le filtre latitude/longitude par MKMapRect avec gestion de l’antiméridien
- [x] Limiter la densité des marqueurs à faible zoom et préparer le clustering
- [x] Remplacer UserDefaults par un cache fichier borné et atomique
- [x] Valider chaînes, dates, NaN, Infinity et données hors limites
- [x] Centraliser exactement le filtrage carte et liste
- [x] Afficher la date et la fraîcheur des données disponibles
- [x] Ne jamais présenter un cache ancien comme absence de risque
- [x] Renforcer la version de synchronisation contre les réponses obsolètes
- [x] Ajouter timeout et remise à zéro de la recherche GPS
- [x] Ajouter les tests déterministes correspondants
- [x] Régénérer, valider et publier la version corrigée

# Corrections Pasted_content_24
- [x] Annuler la Task GPS précédente avant toute nouvelle recherche
- [x] Terminer la recherche GPS sur un fix, une erreur, un refus ou un timeout
- [x] Afficher un message UX explicite après timeout GPS
- [x] Valider schemaVersion et savedAt du cache avant restauration
- [x] Définir une stratégie cohérente de cache mondial ou régional
- [x] Préparer une densité géographique et un clustering pour les grands volumes
- [x] Séparer la confiance de la sévérité et classifier les sources
- [x] Uniformiser le statut Protection active dans Home, Carte, Sécurité et détails
- [x] Clarifier proximité Home versus viewport Carte
- [x] Auditer les états OCR et les devises/FairPrice
- [x] Ajouter les tests déterministes et appareil de l’audit 24
- [x] Régénérer, valider et publier la version corrigée

# Corrections Pasted_content_25
- [x] Lire les sections restantes et cartographier tous les bugs
- [x] Supprimer tout faux résultat scanner et brancher le vrai OCR local
- [x] Gérer caméra, permissions, photo capturée, erreurs et états unknown/error
- [x] Unifier ou désactiver clairement l’ancienne architecture Expo carte
- [x] Filtrer les risques réellement par distance et viewport
- [x] Synchroniser filtre, sélection, liste, carte et zoom
- [x] Préparer clustering et plafonnement avant rendu natif
- [x] Renforcer confiance, provenance, fraîcheur et validation des données
- [x] Auditer offline, alertes, notifications, navigation, sécurité et performance
- [x] Ajouter tests déterministes et matrice appareil complète
- [x] Régénérer, valider, empaqueter et publier la version complète

# Corrections Pasted_content_26
- [x] Cartographier et traiter les 52 points de l’audit
- [x] Créer un RiskRepository et une source publique réelle ou un état indisponible honnête
- [x] Alimenter store, cache et alertes via une seule chaîne de données
- [x] Déplacer le cache critique vers Application Support et gérer migrations/taille/corruption
- [x] Corriger le géofencing au redémarrage, les régions supprimées et les cooldowns
- [x] Structurer preuves, sources, déduplication et rayons par type fiabilité
- [x] Réduire la validité opérationnelle des risques trop anciens et gérer les dates futures
- [x] Corriger faux positifs OCR service/TVA, plusieurs montants, devises et formats
- [x] Séparer arithmétique OCR et FairPrice, implémenter FairPrice ou l’indiquer indisponible
- [x] Corriger zoom, clustering projeté, budget de markers et rayon par type
- [x] Unifier carte/accueil/sécurité et rendre distances dynamiques
- [x] Clarifier l’architecture Expo prototype versus Swift production
- [x] Ajouter provenance, date, explication de fiabilité et accessibilité carte
- [x] Ajouter fixtures et tests pour OCR, GPS, carte, cache et données
- [x] Documenter les tests réellement exécutés versus iPhone/Xcode requis
- [x] Régénérer, valider, empaqueter et publier la version finale

# Corrections Pasted_content_27
- [x] Corriger validated() pour ne pas rejeter un risque à cause d’une preuve ancienne
- [x] Limiter taille HTTP, nombre de risques, doublons ID et rayon d’alerte
- [x] Ajouter source structurée, sourceId, EvidenceType et précision géographique
- [x] Whitelister HTTPS et domaine du feed, valider Content-Type
- [x] Ajouter ETag/304, retry sélectif et réponses réseau versionnées
- [x] Faire choisir le meilleur risque par cellule et stabiliser la grille par zoom
- [x] Interdire geofencing city/country et réconcilier révocation/expiration/rayon
- [x] Migrer confidence legacy, valider preuves uniques et cache intégrité
- [x] Préparer cache régional/viewport et contrat feed paginé
- [x] Ajouter fixtures JSON et tests HTTP/adversariaux
- [x] Régénérer, valider, empaqueter et publier la version finale

# Finalisation complète après audit 27
- [x] Ajouter contrat feed régional par bbox/viewport avec pagination
- [x] Ajouter cache régional borné et clé de tuile stable
- [x] Ajouter fixtures feeds valides, expirées, dupliquées, révoquées, malveillantes et trop volumineuses
- [x] Ajouter tests HTTP des statuts 200, 204, 301, 302, 400, 401, 403, 404, 408, 429, 500, 502, 503
- [x] Vérifier que le cache valide est conservé en cas de réponse invalide
- [x] Régénérer, valider, publier et sauvegarder la version complète

# Dernière passe automatique
- [x] Auditer les validateurs et les scripts de génération actuels
- [x] Durcir les vérifications de sécurité réseau et cache
- [x] Ajouter les tests déterministes encore manquants
- [x] Régénérer, valider, publier et sauvegarder la dernière version

# Audit Pasted_content_28
- [x] Corriger la persistance et l’usage du score serveur de fiabilité
- [x] Corriger les relations preuves/sources et valider les URLs HTTPS autorisées
- [x] Corriger la précision géographique affichée sur la carte
- [x] Corriger la sélection et la validation des geofences
- [x] Corriger le fetch viewport, anti-méridien et cache régional
- [x] Corriger les limites de zoom et interactions de carte
- [x] Auditer et corriger OCR, permissions, onboarding et accès aux réglages
- [x] Ajouter les tests adversariaux de l’audit 28
- [x] Régénérer, valider, synchroniser et sauvegarder la version finale

# Corrections compilation Swift signalées
- [x] Corriger l’interpolation des montants OCR dans ScannerView.swift
- [x] Corriger la portée de centerInitiallyIfNeeded dans RiskMapView.swift
- [x] Régénérer et valider le projet natif après correction

# Nouvelle correction de compilation Swift
- [x] Réécrire les chaînes OCR sans interpolations imbriquées
- [x] Séparer les fonctions de ScannerView et RiskMapView au niveau de type
- [x] Réparer CameraPicker et ses accolades au niveau fichier
- [x] Corriger les if let imbriqués et l’extension OCRSupport
- [x] Régénérer, valider et sauvegarder la version corrigée
