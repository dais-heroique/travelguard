# TravelGuard — Plan d’interface mobile

## Direction produit

TravelGuard doit donner une sensation de **calme, de contrôle et de vigilance discrète**. L’utilisateur est souvent dans une rue inconnue, avec une seule main disponible et peu de temps pour décider. L’interface privilégie donc des cartes lisibles, des actions larges, une hiérarchie visuelle nette et des retours immédiats.

L’expérience cible le portrait mobile 9:16, une utilisation à une main et les conventions iOS : navigation par onglets, feuilles modales, boutons à zones tactiles généreuses, textes courts et actions principales placées dans la moitié basse de l’écran.

## Écrans

| Écran | Contenu principal | Fonctionnalités |
|---|---|---|
| Accueil | Statut de protection, ville détectée, score de vigilance, actions rapides | Ouvrir la carte, scanner, consulter le juste prix, accéder au SOS |
| Carte | Carte centrée sur la zone courante, marqueurs de risques, filtres | Voir les hotspots, filtrer restaurant/taxi/change/attraction, ouvrir une fiche |
| Fiche de lieu | Nom, catégorie, score de confiance, signaux, conseils et sources | Lire les risques, enregistrer, signaler une expérience |
| Scanner | Choix menu / billet / addition, viseur caméra, aperçu de la photo | Capturer ou choisir une image, lancer l’analyse, afficher l’état hors ligne |
| Résultat du scan | Verdict, lignes suspectes, prix observé, juste prix estimé, recommandations | Comparer, marquer comme sûr/suspect, recommencer |
| Juste prix | Recherche par ville et catégorie, cartes de tarifs de référence | Café, taxi, attraction, change ; voir la source et la date |
| Sécurité | Mode hors ligne, alertes, langue locale, téléchargements | Activer les alertes, télécharger une ville, gérer les phrases SOS |
| SOS | Actions police/ambulance, phrases locales, bouton de partage de position | Afficher une phrase, écouter la prononciation, appeler ou partager |
| Réglages | Langue, unités, confidentialité, notifications | Gérer préférences et permissions |

## Navigation

La barre d’onglets comporte quatre destinations principales : **Accueil**, **Carte**, **Scanner** et **Sécurité**. Le **Juste prix** reste accessible depuis l’Accueil et la Carte via une action secondaire persistante. Le bouton SOS apparaît comme un accès d’urgence dans l’onglet Sécurité et comme une action compacte sur l’Accueil ; il ne doit jamais ressembler à une action ordinaire.

## Parcours clés

### Vérifier un lieu

L’utilisateur ouvre TravelGuard, consulte la carte centrée sur sa position, touche un marqueur, lit le score de confiance puis ouvre les signaux détaillés. Il peut enregistrer le lieu ou lancer une vérification de prix.

### Scanner avant de payer

L’utilisateur touche **Scanner**, choisit Menu, Billet ou Addition, cadre le document, capture la photo puis attend un état d’analyse explicite. Le résultat distingue **prix cohérent**, **à vérifier** et **surcoût probable**. Chaque résultat expose les éléments détectés, l’estimation de juste prix et la recommandation d’action.

### Vérifier un taxi

Depuis l’Accueil ou le Juste prix, l’utilisateur choisit la ville, indique la zone de départ et d’arrivée, puis consulte la fourchette officielle. Le résultat précise les suppléments possibles et la date de la source.

### Recevoir une alerte

Après autorisation, l’utilisateur active les alertes locales. Lorsqu’une zone à risque est approchée, une notification courte renvoie vers une fiche d’action : quoi observer, quoi dire, et comment s’éloigner. Le comportement doit rester utile même si la connexion est absente grâce au pack de ville hors ligne.

### Utiliser le SOS

L’utilisateur ouvre Sécurité puis SOS. L’écran met en avant trois actions : appeler les secours, afficher une phrase locale et partager sa position. Les phrases sont présentées en grand texte, avec langue, translittération si disponible et bouton audio.

## Palette de marque

| Élément | Couleur | Usage |
|---|---|---|
| Bleu nuit | `#102A43` | Navigation, titres, confiance |
| Bleu voyage | `#1D6FA5` | Actions principales et liens |
| Turquoise sécurité | `#18A999` | États protégés et confirmations |
| Ambre vigilance | `#F4A261` | À vérifier, attention, surcoût possible |
| Corail alerte | `#E76F51` | Risque élevé et actions SOS secondaires |
| Ivoire | `#F7F4EE` | Fond principal chaleureux |
| Blanc | `#FFFFFF` | Cartes et feuilles modales |
| Encre | `#17202A` | Texte principal |
| Gris brume | `#6B7785` | Texte secondaire et métadonnées |

Le bleu nuit et le turquoise construisent la confiance sans donner une tonalité anxiogène. L’ambre sert à signaler une vérification nécessaire, tandis que le corail est réservé aux risques et au SOS afin de préserver sa valeur d’urgence.

## États et accessibilité

Chaque fonctionnalité doit prévoir les états chargement, succès, indisponible hors ligne, permission refusée et erreur récupérable. Les contrastes doivent rester lisibles en extérieur, les boutons doivent être compréhensibles sans la couleur seule et les textes essentiels doivent respecter une taille confortable pour une lecture rapide.
