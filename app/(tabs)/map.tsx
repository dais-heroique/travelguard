import { useMemo, useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { NativeRiskMap } from "@/components/native-risk-map";
import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { categoryLabels, riskPlaces, scoreTone, type RiskCategory, type RiskPlace } from "@/lib/travelguard-data";
import { useColors } from "@/hooks/use-colors";

const filters: { key: RiskCategory | "all"; label: string }[] = [
  { key: "all", label: "Tout" }, { key: "restaurant", label: "Restaurants" }, { key: "taxi", label: "Taxis" }, { key: "exchange", label: "Change" }, { key: "attraction", label: "Attractions" },
];

export default function MapScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const [selectedFilter, setSelectedFilter] = useState<RiskCategory | "all">("all");
  const [selectedPlace, setSelectedPlace] = useState<RiskPlace | null>(riskPlaces[0]);
  const places = useMemo(() => selectedFilter === "all" ? riskPlaces : riskPlaces.filter((place) => place.category === selectedFilter), [selectedFilter]);

  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <View style={styles.header}><View><Text style={[styles.eyebrow, { color: colors.muted }]}>ZONE DE VIGILANCE</Text><Text style={[styles.title, { color: colors.foreground }]}>Carte des risques</Text></View><View style={[styles.locationBadge, { backgroundColor: colors.surface, borderColor: colors.border }]}><IconSymbol name="location.fill" size={16} color={colors.primary} /><Text style={[styles.locationText, { color: colors.foreground }]}>Paris</Text></View></View>
      <FlatList data={places} keyExtractor={(item) => item.id} showsVerticalScrollIndicator={false} contentContainerStyle={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]} ListHeaderComponent={<>
        <View style={[styles.mapCard, { borderColor: colors.border, backgroundColor: colors.surface }]}><NativeRiskMap places={places} onSelect={setSelectedPlace} /></View>
        <FlatList data={filters} horizontal keyExtractor={(item) => item.key} showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterList} renderItem={({ item }) => <Pressable onPress={() => setSelectedFilter(item.key)} style={({ pressed }) => [styles.filter, { backgroundColor: selectedFilter === item.key ? colors.primary : colors.surface, borderColor: selectedFilter === item.key ? colors.primary : colors.border }, pressed && { opacity: 0.75 }]}><Text style={[styles.filterText, { color: selectedFilter === item.key ? "#FFFFFF" : colors.foreground }]}>{item.label}</Text></Pressable>} />
        <View style={styles.sectionHeader}><Text style={[styles.sectionTitle, { color: colors.foreground }]}>Signaux à proximité</Text><Text style={[styles.count, { color: colors.muted }]}>{places.length} lieux</Text></View>
      </>} renderItem={({ item }) => <Pressable onPress={() => setSelectedPlace(item)} style={({ pressed }) => [styles.placeRow, { backgroundColor: colors.surface, borderColor: colors.border }, pressed && { opacity: 0.75 }]}><View style={[styles.scoreCircle, { borderColor: scoreTone(item.score).color }]}><Text style={[styles.scoreText, { color: scoreTone(item.score).color }]}>{item.score}</Text></View><View style={styles.placeCopy}><Text style={[styles.placeName, { color: colors.foreground }]}>{item.name}</Text><Text style={[styles.placeMeta, { color: colors.muted }]}>{categoryLabels[item.category]} · {item.distance}</Text><Text style={[styles.placeSummary, { color: colors.muted }]} numberOfLines={1}>{item.summary}</Text></View><IconSymbol name="chevron.right" size={18} color={colors.muted} /></Pressable>} ListFooterComponent={selectedPlace ? <View style={[styles.detailCard, { backgroundColor: colors.primary }]}><View style={styles.detailTop}><Text style={styles.detailCategory}>{categoryLabels[selectedPlace.category].toUpperCase()}</Text><Text style={styles.detailScore}>{selectedPlace.score}/100</Text></View><Text style={styles.detailName}>{selectedPlace.name}</Text><Text style={styles.detailSummary}>{selectedPlace.summary}</Text><View style={styles.signalWrap}>{selectedPlace.signals.map((signal) => <View key={signal} style={styles.signal}><View style={styles.signalDot} /><Text style={styles.signalText}>{signal}</Text></View>)}</View></View> : null} />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 20, paddingTop: 18, flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  eyebrow: { fontSize: 11, fontWeight: "800", letterSpacing: 1.4 },
  title: { fontSize: 27, lineHeight: 34, fontWeight: "800", marginTop: 5 },
  locationBadge: { flexDirection: "row", alignItems: "center", gap: 5, borderWidth: 1, borderRadius: 14, paddingHorizontal: 10, paddingVertical: 8 },
  locationText: { fontSize: 12, fontWeight: "800" },
  content: { padding: 20, paddingTop: 18, paddingBottom: 32 },
  mapCard: { height: 240, borderRadius: 24, overflow: "hidden", borderWidth: 1 },
  filterList: { gap: 8, paddingVertical: 16 },
  filter: { paddingHorizontal: 14, paddingVertical: 9, borderRadius: 14, borderWidth: 1 },
  filterText: { fontSize: 12, fontWeight: "800" },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  sectionTitle: { fontSize: 18, fontWeight: "800" },
  count: { fontSize: 12, fontWeight: "700" },
  placeRow: { minHeight: 78, borderRadius: 17, borderWidth: 1, marginBottom: 9, padding: 12, flexDirection: "row", alignItems: "center" },
  scoreCircle: { width: 45, height: 45, borderRadius: 23, borderWidth: 3, alignItems: "center", justifyContent: "center", marginRight: 11 },
  scoreText: { fontSize: 15, fontWeight: "800" },
  placeCopy: { flex: 1 },
  placeName: { fontSize: 14, fontWeight: "800" },
  placeMeta: { fontSize: 11, marginTop: 3 },
  placeSummary: { fontSize: 11, marginTop: 4 },
  detailCard: { borderRadius: 20, padding: 18, marginTop: 6 },
  detailTop: { flexDirection: "row", justifyContent: "space-between" },
  detailCategory: { color: "#B8F3E5", fontSize: 10, fontWeight: "800", letterSpacing: 1.1 },
  detailScore: { color: "#FFFFFF", fontWeight: "800", fontSize: 13 },
  detailName: { color: "#FFFFFF", fontSize: 20, fontWeight: "800", marginTop: 10 },
  detailSummary: { color: "#D9F2F1", fontSize: 13, lineHeight: 19, marginTop: 4 },
  signalWrap: { marginTop: 14, gap: 8 },
  signal: { flexDirection: "row", alignItems: "center", gap: 8 },
  signalDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: "#F4A261" },
  signalText: { color: "#FFFFFF", fontSize: 12, flex: 1 },
});
