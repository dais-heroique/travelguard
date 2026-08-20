export type RiskCategory = "restaurant" | "taxi" | "exchange" | "attraction";

export type RiskPlace = {
  id: string;
  name: string;
  category: RiskCategory;
  coordinate: { latitude: number; longitude: number };
  score: number;
  summary: string;
  signals: string[];
  sourceType: "government" | "partner" | "community" | "unknown";
  source: string;
  updatedAt: string;
};

export type FairPriceItem = {
  id: string;
  label: string;
  category: string;
  value: string;
  reference: string;
  updated: string;
  source: string;
};

// L’architecture Expo n’est pas la cible de production. Aucune donnée statique n’est exposée ici.
// La source canonique est TravelGuardStore dans le paquet Swift natif.
export const riskPlaces: RiskPlace[] = [];
export const fairPrices: FairPriceItem[] = [];

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
  if (score < 25) return { label: "Faible", color: "#35A77C" };
  if (score < 60) return { label: "Modéré", color: "#F4A261" };
  if (score < 80) return { label: "Élevé", color: "#E76F51" };
  return { label: "Critique", color: "#7B61A8" };
}
