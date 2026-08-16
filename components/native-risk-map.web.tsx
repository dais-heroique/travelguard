import { Pressable, StyleSheet, Text, View } from "react-native";

import { IconSymbol } from "@/components/ui/icon-symbol";
import { scoreTone, type RiskPlace } from "@/lib/travelguard-data";
import { useColors } from "@/hooks/use-colors";

export function NativeRiskMap({ places, onSelect }: { places: RiskPlace[]; onSelect: (place: RiskPlace) => void }) {
  const colors = useColors();
  return (
    <View style={styles.map}>
      <View style={[styles.grid, { borderColor: `${colors.primary}20` }]} />
      {places.map((place, index) => <Pressable key={place.id} style={[styles.pin, { left: `${22 + index * 19}%`, top: `${25 + (index % 2) * 24}%`, backgroundColor: scoreTone(place.score).color }]} onPress={() => onSelect(place)}><IconSymbol name="location.fill" size={18} color="#FFFFFF" /></Pressable>)}
      <View style={styles.label}><Text style={styles.labelText}>Zone actuelle</Text></View>
    </View>
  );
}

const styles = StyleSheet.create({
  map: { flex: 1, backgroundColor: "#E5EFF2", position: "relative", overflow: "hidden" },
  grid: { ...StyleSheet.absoluteFillObject, opacity: 0.3, borderWidth: 18, borderStyle: "dashed", transform: [{ rotate: "12deg" }, { scale: 1.4 }] },
  pin: { position: "absolute", width: 34, height: 34, borderRadius: 17, alignItems: "center", justifyContent: "center", borderWidth: 3, borderColor: "#FFFFFF" },
  label: { position: "absolute", bottom: 14, left: 14, backgroundColor: "#102A43E8", paddingHorizontal: 10, paddingVertical: 7, borderRadius: 10 },
  labelText: { color: "#FFFFFF", fontSize: 11, fontWeight: "800" },
});
