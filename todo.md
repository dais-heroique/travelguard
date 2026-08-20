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
