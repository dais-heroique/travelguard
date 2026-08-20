# Sources officielles TravelGuard

TravelGuard référence désormais des sources publiques officielles dans l’écran **Sécurité**, sans présenter de données de démonstration comme des tarifs ou des risques locaux vérifiés.

| Source | Contenu | Limite d’usage |
|---|---|---|
| [U.S. Department of State — Scams](https://travel.state.gov/en/international-travel/travel-advisories/scams.html) | Conseils officiels et exemples d’arnaques de voyage | Source générale orientée voyageurs américains ; elle ne fournit pas de points géographiques locaux par établissement |
| [U.S. Department of State — Travel Advisories](https://travel.state.gov/en/international-travel/travel-advisories.html) | Avertissements par pays et niveaux de prudence | Niveau national, pas un indice de prix ni une carte de pièges touristiques |
| [FTC — Avoid Scams When You Travel](https://consumer.ftc.gov/articles/avoid-scams-when-you-travel) | Signaux d’arnaque, frais cachés et moyens de paiement à risque | Conseils consommateurs américains, sans tarifs locaux universels |
| [Data.gov — Travel Advisories](https://catalog.data.gov/dataset/travel-advisories) | Catalogue public et flux d’avertissements du Department of State | Le catalogue indique une mise à jour de dataset ancienne ; il doit être synchronisé avec prudence |
| [NYC Taxi & Limousine Commission — Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page) | Données de courses de taxis et composantes de tarifs à New York | Données propres à New York, statistiques de trajets et non barème universel ; l’autorité précise ses limites de précision |

## Décision produit

Aucun jeu de données officiel mondial, homogène et autorisé ne fournit simultanément les pièges touristiques géolocalisés, les prix de cafés, les tarifs de taxis et les billets d’attraction pour toutes les villes. L’application affiche donc un état **« aucune donnée officielle disponible pour cette ville »** plutôt que d’inventer une référence. Les données de démonstration sont conservées uniquement dans le code de génération pour des tests visuels et ne sont pas utilisées par les écrans natifs.

Le scanner Vision réalise une extraction locale structurée du sous-total, des taxes, du service et du total lorsqu’ils sont lisibles. Il compare la somme des lignes détectées avec le total imprimé, mais ne prétend pas établir un « juste prix » officiel sans référence de ville sourcée.
