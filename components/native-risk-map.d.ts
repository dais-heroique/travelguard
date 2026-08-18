export type RiskMapUserLocation = { latitude: number; longitude: number };
export type NativeRiskMapProps = {
  places: import("@/lib/travelguard-data").RiskPlace[];
  userLocation?: RiskMapUserLocation;
  onSelect: (place: import("@/lib/travelguard-data").RiskPlace) => void;
};
export { NativeRiskMap } from "./native-risk-map.native";
