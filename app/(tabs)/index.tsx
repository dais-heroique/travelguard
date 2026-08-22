import { router } from "expo-router";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { fairPrices } from "@/lib/travelguard-data";
import { useColors } from "@/hooks/use-colors";
import { formatTravelPlace, useNetworkStatus, useTravelLocation } from "@/hooks/use-travel-status";

const actions = [
  { label: "Voir la carte", detail: "Pièges autour de vous", icon: "map.fill" as const, route: "/(tabs)/map" },
  { label: "Scanner", detail: "Menu, billet ou addition", icon: "viewfinder" as const, route: "/(tabs)/scanner" },
  { label: "Juste prix", detail: "Comparer avant de payer", icon: "checkmark.seal.fill" as const, route: "/(tabs)/safety" },
];

export default function HomeScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const { isOnline, isChecking } = useNetworkStatus();
  const { location, permissionDenied, isLoading: isLocationLoading } = useTravelLocation();
  const placeLabel = formatTravelPlace(location);
  const connectionLabel = isChecking ? "Vérification de la connexion…" : isOnline ? "Protection active · connexion disponible" : "Mode hors ligne · données locales";

  return (
    <ScreenContainer className="px-5" containerClassName="bg-background">
      <FlatList
        data={fairPrices.slice(0, 3)}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]}
        ListHeaderComponent={
          <View>
            <View style={styles.headerRow}>
              <View>
                <Text style={[styles.eyebrow, { color: colors.muted }]}>TRAVELGUARD</Text>
                <Text style={[styles.title, { color: colors.foreground }]}>Voyagez l’esprit léger.</Text>
              </View>
              <View style={[styles.avatar, { backgroundColor: colors.primary }]}><Text style={styles.avatarText}>TG</Text></View>
            </View>

            <View style={[styles.protectionCard, { backgroundColor: colors.primary }]}>
              <View style={styles.cardTopLine}><View style={[styles.liveDot, { backgroundColor: isOnline ? colors.success : colors.warning }]} /><Text style={styles.cardKicker}>{isChecking ? "VÉRIFICATION EN COURS" : isOnline ? "PROTECTION DISPONIBLE" : "MODE HORS LIGNE"}</Text></View>
              <Text style={styles.protectionTitle}>{isLocationLoading ? "Localisation en cours…" : placeLabel}</Text>
              <Text style={styles.protectionCopy}>{permissionDenied ? "Autorisez la localisation dans Réglages pour afficher les contrôles autour de vous." : connectionLabel}</Text>
              <Pressable style={({ pressed }) => [styles.cardButton, pressed && styles.pressed]} onPress={() => router.push("/(tabs)/map" as never)}>
                <Text style={styles.cardButtonText}>Explorer la zone</Text><IconSymbol name="chevron.right" size={18} color="#102A43" />
              </Pressable>
            </View>

            <Text style={[styles.sectionTitle, { color: colors.foreground }]}>Besoin d’un contrôle rapide ?</Text>
            <View style={styles.actionGrid}>
              {actions.map((action) => (
                <Pressable key={action.label} style={({ pressed }) => [styles.actionCard, { backgroundColor: colors.surface, borderColor: colors.border }, pressed && styles.pressed]} onPress={() => router.push(action.route as never)}>
                  <View style={[styles.actionIcon, { backgroundColor: `${colors.primary}18` }]}><IconSymbol name={action.icon} size={22} color={colors.primary} /></View>
                  <Text style={[styles.actionLabel, { color: colors.foreground }]}>{action.label}</Text>
                  <Text style={[styles.actionDetail, { color: colors.muted }]}>{action.detail}</Text>
                </Pressable>
              ))}
            </View>

            <View style={styles.sectionHeader}><Text style={[styles.sectionTitle, { color: colors.foreground }]}>Juste prix près de vous</Text><Pressable onPress={() => router.push("/(tabs)/safety" as never)}><Text style={[styles.link, { color: colors.primary }]}>Tout voir</Text></Pressable></View>
          </View>
        }
        renderItem={({ item }) => (
          <View style={[styles.priceRow, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.priceIcon}><IconSymbol name="checkmark.seal.fill" size={18} color={colors.success} /></View>
            <View style={styles.priceCopy}><Text style={[styles.priceLabel, { color: colors.foreground }]}>{item.label}</Text><Text style={[styles.priceMeta, { color: colors.muted }]}>{item.reference}</Text></View>
            <Text style={[styles.priceValue, { color: colors.foreground }]}>{item.value}</Text>
          </View>
        )}
        ListFooterComponent={<Pressable style={({ pressed }) => [styles.sosButton, { backgroundColor: colors.error }, pressed && styles.pressed]} onPress={() => router.push("/(tabs)/safety" as never)}><IconSymbol name="shield.fill" size={20} color="#FFFFFF" /><Text style={styles.sosText}>SOS et phrases locales</Text></Pressable>}
      />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { paddingTop: 6, paddingBottom: 32, gap: 12 },
  headerRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 20 },
  eyebrow: { fontSize: 12, fontWeight: "800", letterSpacing: 1.6 },
  title: { fontSize: 27, lineHeight: 33, fontWeight: "800", marginTop: 6, maxWidth: 270 },
  avatar: { width: 42, height: 42, borderRadius: 21, alignItems: "center", justifyContent: "center" },
  avatarText: { color: "#FFFFFF", fontWeight: "800", fontSize: 13 },
  protectionCard: { borderRadius: 24, padding: 20, marginBottom: 24 },
  cardTopLine: { flexDirection: "row", alignItems: "center", gap: 8 },
  liveDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#B8F3E5" },
  cardKicker: { color: "#DDFBF4", fontSize: 11, fontWeight: "800", letterSpacing: 1.1 },
  protectionTitle: { color: "#FFFFFF", fontSize: 24, fontWeight: "800", marginTop: 18 },
  protectionCopy: { color: "#D9F2F1", fontSize: 14, lineHeight: 20, marginTop: 6, maxWidth: 290 },
  cardButton: { marginTop: 18, borderRadius: 14, backgroundColor: "#FFFFFF", paddingVertical: 12, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  cardButtonText: { color: "#102A43", fontSize: 14, fontWeight: "800" },
  sectionTitle: { fontSize: 18, fontWeight: "800", marginBottom: 12 },
  actionGrid: { flexDirection: "row", gap: 9, marginBottom: 24 },
  actionCard: { flex: 1, minHeight: 134, borderRadius: 18, borderWidth: 1, padding: 12 },
  actionIcon: { width: 38, height: 38, borderRadius: 12, alignItems: "center", justifyContent: "center", marginBottom: 12 },
  actionLabel: { fontWeight: "800", fontSize: 14 },
  actionDetail: { fontSize: 11, lineHeight: 15, marginTop: 5 },
  sectionHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 2 },
  link: { fontSize: 13, fontWeight: "800", marginBottom: 12 },
  priceRow: { minHeight: 68, borderRadius: 16, borderWidth: 1, padding: 12, flexDirection: "row", alignItems: "center", marginBottom: 9 },
  priceIcon: { width: 34, height: 34, borderRadius: 12, backgroundColor: "#18A99918", alignItems: "center", justifyContent: "center", marginRight: 10 },
  priceCopy: { flex: 1 },
  priceLabel: { fontSize: 14, fontWeight: "800" },
  priceMeta: { fontSize: 11, marginTop: 3 },
  priceValue: { fontSize: 14, fontWeight: "800" },
  sosButton: { borderRadius: 16, minHeight: 52, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, marginTop: 8 },
  sosText: { color: "#FFFFFF", fontSize: 14, fontWeight: "800" },
  pressed: { opacity: 0.78, transform: [{ scale: 0.98 }] },
});
