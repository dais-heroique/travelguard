import { Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";

export default function SafetyScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <View style={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]}>
        <Text style={[styles.eyebrow, { color: colors.muted }]}>PROTECTION ET RÉFÉRENCES</Text>
        <Text style={[styles.title, { color: colors.foreground }]}>Sécurité</Text>
        <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <Text style={[styles.cardTitle, { color: colors.foreground }]}>Fonctions de production dans l’app native</Text>
          <Text style={[styles.cardCopy, { color: colors.muted }]}>Les autorisations GPS, les notifications, le SOS, les risques synchronisés, le cache hors ligne et les références officielles sont gérés par le paquet Swift TravelGuard.xcodeproj. Cet aperçu Expo ne prétend pas avoir activé des alertes.</Text>
          <Text style={[styles.status, { color: colors.warning }]}>Alertes non disponibles dans l’aperçu Expo.</Text>
        </View>
        <View style={[styles.sos, { backgroundColor: colors.error }]}>
          <Text style={styles.sosTitle}>Besoin d’aide ?</Text>
          <Text style={styles.sosCopy}>Utilisez les phrases SOS et le numéro d’urgence adaptés à votre position dans l’app native.</Text>
        </View>
        <Pressable style={[styles.action, { backgroundColor: colors.primary }]}><Text style={styles.actionText}>Ouvrir le projet natif dans Xcode</Text></Pressable>
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 18 },
  eyebrow: { fontSize: 10, fontWeight: "800", letterSpacing: 1.2 },
  title: { fontSize: 28, fontWeight: "800", marginTop: 6 },
  card: { borderRadius: 22, borderWidth: 1, padding: 20, marginTop: 24 },
  cardTitle: { fontSize: 20, fontWeight: "800" },
  cardCopy: { fontSize: 14, lineHeight: 21, marginTop: 10 },
  status: { fontSize: 13, fontWeight: "800", marginTop: 16 },
  sos: { borderRadius: 22, padding: 20, marginTop: 14 },
  sosTitle: { color: "#FFFFFF", fontSize: 20, fontWeight: "800" },
  sosCopy: { color: "#FFE8E2", fontSize: 14, lineHeight: 20, marginTop: 8 },
  action: { minHeight: 56, borderRadius: 18, marginTop: 16, alignItems: "center", justifyContent: "center", paddingHorizontal: 16 },
  actionText: { color: "#FFFFFF", fontSize: 14, fontWeight: "800" },
});
