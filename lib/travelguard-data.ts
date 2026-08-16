export type RiskCategory = "restaurant" | "taxi" | "exchange" | "attraction";

export type RiskPlace = {
  id: string;
  name: string;
  category: RiskCategory;
  coordinate: { latitude: number; longitude: number };
  score: number;
  distance: string;
  summary: string;
  signals: string[];
};

export type FairPriceItem = {
  id: string;
  label: string;
  category: string;
  value: string;
  reference: string;
  updated: string;
};

export const riskPlaces: RiskPlace[] = [
  {
    id: "cafe-signal",
    name: "Café du Passage",
    category: "restaurant",
    coordinate: { latitude: 48.8584, longitude: 2.2945 },
    score: 38,
    distance: "350 m",
    summary: "Menu touristique signalé par des voyageurs.",
    signals: ["Prix affichés uniquement à l’intérieur", "Menu sans devise claire", "Deux signalements récents"],
  },
  {
    id: "taxi-nord",
    name: "Station taxi — Nord",
    category: "taxi",
    coordinate: { latitude: 48.8612, longitude: 2.2971 },
    score: 72,
    distance: "620 m",
    summary: "Station officielle, tarif réglementé à vérifier selon l’horaire.",
    signals: ["Station identifiée", "Tarif de nuit possible", "Reçu recommandé"],
  },
  {
    id: "change-central",
    name: "Change Central",
    category: "exchange",
    coordinate: { latitude: 48.8568, longitude: 2.301 },
    score: 46,
    distance: "900 m",
    summary: "Écart important entre le taux affiché et le taux de référence.",
    signals: ["Commission peu visible", "Taux de vente à comparer", "Demander le montant net"],
  },
  {
    id: "ticket-quai",
    name: "Billetterie du Quai",
    category: "attraction",
    coordinate: { latitude: 48.8551, longitude: 2.2918 },
    score: 84,
    distance: "1,2 km",
    summary: "Point de vente correctement identifié, mais billets officiels conseillés.",
    signals: ["Site officiel disponible", "Pas de frais cachés détectés", "Réservation en ligne possible"],
  },
];

export const fairPrices: FairPriceItem[] = [
  { id: "coffee", label: "Café filtre", category: "Restaurant", value: "2,80 €", reference: "Référence locale moyenne", updated: "Mise à jour il y a 4 j" },
  { id: "taxi", label: "Course taxi — 3 km", category: "Transport", value: "11–15 €", reference: "Tarif réglementé estimé", updated: "Mise à jour il y a 2 j" },
  { id: "museum", label: "Billet musée", category: "Attraction", value: "16 €", reference: "Tarif officiel adulte", updated: "Mise à jour il y a 7 j" },
  { id: "exchange", label: "Commission change", category: "Change", value: "0–3 %", reference: "Fourchette transparente", updated: "Mise à jour il y a 5 j" },
];

export const sosPhrases = [
  { local: "Je veux le reçu, s’il vous plaît.", translation: "I would like the receipt, please.", language: "Français" },
  { local: "Quel est le tarif officiel ?", translation: "What is the official fare?", language: "Français" },
  { local: "Appelez la police, s’il vous plaît.", translation: "Please call the police.", language: "Français" },
];

export const categoryLabels: Record<RiskCategory, string> = {
  restaurant: "Restaurants",
  taxi: "Taxis",
  exchange: "Change",
  attraction: "Attractions",
};

export function scoreTone(score: number) {
  if (score < 50) return { label: "Vigilance élevée", color: "#E76F51" };
  if (score < 75) return { label: "À vérifier", color: "#F4A261" };
  return { label: "Confiance correcte", color: "#18A999" };
}
