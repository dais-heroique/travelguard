import { Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";

export default function MapScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <View style={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]}>
        <Text style={[styles.eyebrow, { color: colors.muted }]}>ZONE DE VIGILANCE</Text>
        <Text style={[styles.title, { color: colors.foreground }]}>Carte des risques</Text>
        <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.foreground }]}>Carte native canonique</Text>
          <Text style={[styles.cardCopy, { color: colors.muted }]}>La carte fiable de TravelGuard est intégrée à TravelGuard.xcodeproj. Elle utilise le GPS, le cache validé, le viewport MapKit et les risques synchronisés. Cet aperçu Expo n’affiche aucune donnée statique ni distance inventée.</Text>
          <Text style={[styles.state, { color: colors.warning }]}>Aucune donnée cartographique disponible dans l’aperçu Expo.</Text>
        </View>
        <Pressable style={[styles.action, { backgroundColor: colors.primary }]}><Text style={styles.actionText}>Ouvrir le projet natif dans Xcode</Text></Pressable>
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 18 },
  eyebrow: { fontSize: 11, fontWeight: "800", letterSpacing: 1.4 },
  title: { fontSize: 28, lineHeight: 35, fontWeight: "800", marginTop: 6 },
  card: { borderRadius: 22, borderWidth: 1, padding: 20, marginTop: 24 },
  cardTitle: { fontSize: 20, fontWeight: "800" },
  cardCopy: { fontSize: 14, lineHeight: 21, marginTop: 10 },
  state: { fontSize: 13, lineHeight: 18, fontWeight: "700", marginTop: 16 },
  action: { minHeight: 56, borderRadius: 18, marginTop: 16, alignItems: "center", justifyContent: "center", paddingHorizontal: 16 },
  actionText: { color: "#FFFFFF", fontSize: 14, fontWeight: "800" },
});
