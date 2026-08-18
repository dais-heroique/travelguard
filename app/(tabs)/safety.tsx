import { useState } from "react";
import * as Location from "expo-location";
import { Alert, FlatList, Linking, Pressable, StyleSheet, Switch, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { fairPrices, sosPhrases } from "@/lib/travelguard-data";
import { useColors } from "@/hooks/use-colors";
import { useNetworkStatus, useTravelLocation } from "@/hooks/use-travel-status";

export default function SafetyScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const [alertsEnabled, setAlertsEnabled] = useState(true);
  const { isOnline, isChecking } = useNetworkStatus();
  const { location } = useTravelLocation();
  const offlineActive = !isChecking && !isOnline;
  const cityLabel = location?.city ?? "Ville à localiser";
  const [activePhrase, setActivePhrase] = useState(0);

  async function handleAlertsChange(value: boolean) {
    if (!value) {
      setAlertsEnabled(false);
      return;
    }
    const permission = await Location.requestForegroundPermissionsAsync();
    if (permission.granted) {
      setAlertsEnabled(true);
      return;
    }
    Alert.alert("Localisation nécessaire", "Autorisez la localisation dans Réglages pour recevoir les alertes à proximité.");
  }

  function callEmergency() {
    Alert.alert("Appel d’urgence", "Choisissez le service d’urgence local à appeler.", [{ text: "Annuler", style: "cancel" }, { text: "Police", onPress: () => Linking.openURL("tel:112") }]);
  }

  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <FlatList data={fairPrices} keyExtractor={(item) => item.id} contentContainerStyle={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]} showsVerticalScrollIndicator={false} ListHeaderComponent={<>
        <View style={styles.header}><View><Text style={[styles.eyebrow, { color: colors.muted }]}>PROTECTION ET RÉFÉRENCES</Text><Text style={[styles.title, { color: colors.foreground }]}>Sécurité</Text></View><View style={[styles.safeBadge, { backgroundColor: `${colors.success}18` }]}><IconSymbol name="shield.fill" size={17} color={colors.success} /><Text style={[styles.safeText, { color: colors.success }]}>Active</Text></View></View>
        <View style={[styles.sosCard, { backgroundColor: colors.error }]}><View style={styles.sosTop}><View><Text style={styles.sosKicker}>BESOIN D’AIDE ?</Text><Text style={styles.sosTitle}>Gardez vos phrases prêtes.</Text></View><IconSymbol name="shield.fill" size={28} color="#FFFFFF" /></View><Text style={styles.sosCopy}>Affichez une phrase locale ou contactez les secours sans chercher dans vos réglages.</Text><View style={styles.sosActions}><Pressable onPress={callEmergency} style={({ pressed }) => [styles.sosAction, pressed && { opacity: 0.75 }]}><IconSymbol name="phone.fill" size={18} color={colors.error} /><Text style={styles.sosActionText}>Secours</Text></Pressable><Pressable onPress={() => setActivePhrase((activePhrase + 1) % sosPhrases.length)} style={({ pressed }) => [styles.sosAction, pressed && { opacity: 0.75 }]}><IconSymbol name="speaker.wave.2.fill" size={18} color={colors.error} /><Text style={styles.sosActionText}>Phrase locale</Text></Pressable></View></View>
        <View style={[styles.phraseCard, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={styles.phraseHeader}><Text style={[styles.sectionTitle, { color: colors.foreground }]}>À afficher maintenant</Text><Text style={[styles.language, { color: colors.primary }]}>{sosPhrases[activePhrase].language}</Text></View><Text style={[styles.phraseLocal, { color: colors.foreground }]}>{sosPhrases[activePhrase].local}</Text><Text style={[styles.phraseTranslation, { color: colors.muted }]}>{sosPhrases[activePhrase].translation}</Text><Pressable onPress={() => setActivePhrase((activePhrase + 1) % sosPhrases.length)} style={({ pressed }) => [styles.nextPhrase, { borderColor: colors.border }, pressed && { opacity: 0.75 }]}><IconSymbol name="arrow.clockwise" size={16} color={colors.primary} /><Text style={[styles.nextPhraseText, { color: colors.primary }]}>Changer de phrase</Text></Pressable></View>
        <Text style={[styles.sectionTitle, { color: colors.foreground }]}>Réglages de protection</Text>
        <View style={[styles.settingsCard, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={styles.settingRow}><View style={[styles.settingIcon, { backgroundColor: `${colors.primary}18` }]}><IconSymbol name="location.fill" size={19} color={colors.primary} /></View><View style={styles.settingCopy}><Text style={[styles.settingTitle, { color: colors.foreground }]}>Alertes à proximité</Text><Text style={[styles.settingSub, { color: colors.muted }]}>Signaux de risque autour de votre position</Text></View><Switch value={alertsEnabled} onValueChange={handleAlertsChange} trackColor={{ false: colors.border, true: `${colors.success}80` }} thumbColor={alertsEnabled ? colors.success : "#FFFFFF"} /></View><View style={[styles.divider, { backgroundColor: colors.border }]} /><View style={styles.settingRow}><View style={[styles.settingIcon, { backgroundColor: `${colors.primary}18` }]}><IconSymbol name="wifi.slash" size={19} color={offlineActive ? colors.warning : colors.success} /></View><View style={styles.settingCopy}><Text style={[styles.settingTitle, { color: colors.foreground }]}>Mode hors ligne automatique</Text><Text style={[styles.settingSub, { color: colors.muted }]}>{isChecking ? "Vérification de la connexion…" : isOnline ? "Connexion active · les données locales restent prêtes" : "Aucune connexion · données locales utilisées"}</Text></View><Switch value={offlineActive} disabled trackColor={{ false: colors.border, true: `${colors.warning}80` }} thumbColor={offlineActive ? colors.warning : "#FFFFFF"} /></View></View>
        <View style={styles.priceHeader}><Text style={[styles.sectionTitle, { color: colors.foreground }]}>Indice du juste prix</Text><Text style={[styles.city, { color: colors.muted }]}>{cityLabel} · EUR</Text></View>
      </>} renderItem={({ item }) => <View style={[styles.priceRow, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={[styles.priceIcon, { backgroundColor: `${colors.success}18` }]}><IconSymbol name="checkmark.seal.fill" size={18} color={colors.success} /></View><View style={styles.priceCopy}><Text style={[styles.priceLabel, { color: colors.foreground }]}>{item.label}</Text><Text style={[styles.priceMeta, { color: colors.muted }]}>{item.reference} · {item.updated}</Text></View><Text style={[styles.priceValue, { color: colors.foreground }]}>{item.value}</Text></View>} ListFooterComponent={<Text style={[styles.disclaimer, { color: colors.muted }]}>Les références sont indicatives. Vérifiez toujours la source officielle et les conditions locales avant de payer.</Text>} />
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { paddingHorizontal: 20, paddingTop: 6, paddingBottom: 34 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 20 },
  eyebrow: { fontSize: 10, fontWeight: "800", letterSpacing: 1.2 },
  title: { fontSize: 28, fontWeight: "800", marginTop: 5 },
  safeBadge: { flexDirection: "row", gap: 6, alignItems: "center", borderRadius: 13, paddingHorizontal: 10, paddingVertical: 8 },
  safeText: { fontSize: 12, fontWeight: "800" },
  sosCard: { borderRadius: 23, padding: 18, marginBottom: 14 },
  sosTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" },
  sosKicker: { color: "#FFD5CC", fontSize: 10, fontWeight: "800", letterSpacing: 1.1 },
  sosTitle: { color: "#FFFFFF", fontSize: 20, fontWeight: "800", marginTop: 7, maxWidth: 240 },
  sosCopy: { color: "#FFE8E2", fontSize: 13, lineHeight: 18, marginTop: 12 },
  sosActions: { flexDirection: "row", gap: 9, marginTop: 16 },
  sosAction: { flex: 1, height: 42, backgroundColor: "#FFFFFF", borderRadius: 13, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 7 },
  sosActionText: { color: "#E76F51", fontSize: 12, fontWeight: "800" },
  phraseCard: { borderRadius: 19, borderWidth: 1, padding: 16, marginBottom: 22 },
  phraseHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  sectionTitle: { fontSize: 18, fontWeight: "800", marginBottom: 11 },
  language: { fontSize: 11, fontWeight: "800" },
  phraseLocal: { fontSize: 21, lineHeight: 28, fontWeight: "800", marginTop: 7 },
  phraseTranslation: { fontSize: 13, lineHeight: 18, marginTop: 4 },
  nextPhrase: { borderWidth: 1, borderRadius: 12, minHeight: 38, marginTop: 14, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 7 },
  nextPhraseText: { fontSize: 12, fontWeight: "800" },
  settingsCard: { borderRadius: 19, borderWidth: 1, paddingHorizontal: 14, marginBottom: 22 },
  settingRow: { minHeight: 74, flexDirection: "row", alignItems: "center" },
  settingIcon: { width: 38, height: 38, borderRadius: 12, alignItems: "center", justifyContent: "center", marginRight: 11 },
  settingCopy: { flex: 1, paddingRight: 8 },
  settingTitle: { fontSize: 14, fontWeight: "800" },
  settingSub: { fontSize: 11, lineHeight: 15, marginTop: 3 },
  divider: { height: 1 },
  priceHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 2 },
  city: { fontSize: 12, fontWeight: "700", marginBottom: 11 },
  priceRow: { minHeight: 70, borderRadius: 16, borderWidth: 1, padding: 12, flexDirection: "row", alignItems: "center", marginBottom: 9 },
  priceIcon: { width: 34, height: 34, borderRadius: 12, alignItems: "center", justifyContent: "center", marginRight: 10 },
  priceCopy: { flex: 1 },
  priceLabel: { fontSize: 14, fontWeight: "800" },
  priceMeta: { fontSize: 10, lineHeight: 14, marginTop: 3 },
  priceValue: { fontSize: 14, fontWeight: "800" },
  disclaimer: { fontSize: 11, lineHeight: 16, marginTop: 7 },
});
