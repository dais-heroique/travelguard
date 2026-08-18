import AsyncStorage from "@react-native-async-storage/async-storage";
import { router } from "expo-router";
import * as Location from "expo-location";
import { useMemo, useState } from "react";
import { Alert, Linking, Platform, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";

const steps = [
  { eyebrow: "BIENVENUE DANS TRAVELGUARD", title: "Votre bouclier avant de payer.", body: "Dans une ville inconnue, les bons réflexes doivent être accessibles en quelques secondes. TravelGuard vous aide à repérer les signaux faibles avant qu’ils ne coûtent cher.", icon: "shield.fill" as const, action: "Découvrir la protection" },
  { eyebrow: "VOTRE VOYAGE", title: "Quel voyageur êtes-vous ?", body: "Cela nous aide à mettre les bonnes alertes en avant. Vous pourrez modifier vos choix plus tard.", icon: "person.fill" as const, action: "Continuer" },
  { eyebrow: "VOS PRIORITÉS", title: "Que voulez-vous éviter ?", body: "Sélectionnez les situations qui vous préoccupent le plus pour personnaliser votre carte et vos conseils.", icon: "checkmark.seal.fill" as const, action: "Enregistrer mes priorités" },
  { eyebrow: "LE SCANNER", title: "Un prix vous semble étrange ?", body: "Cadrez un menu, une addition ou un billet. Le scanner compare les éléments visibles avec le juste prix disponible pour votre destination.", icon: "viewfinder" as const, action: "Voir comment ça marche" },
  { eyebrow: "LE JUSTE PRIX", title: "Comprendre avant d’accepter.", body: "Café, taxi, attraction ou change : consultez une référence locale, sa date et les suppléments possibles.", icon: "checkmark.seal.fill" as const, action: "Activer mes références" },
  { eyebrow: "HORS LIGNE", title: "Même sans réseau, vous restez prêt.", body: "Le pack de destination garde vos repères essentiels, vos phrases SOS et les signaux déjà téléchargés sur votre téléphone.", icon: "wifi.slash" as const, action: "Préparer mon mode hors ligne" },
  { eyebrow: "ALERTES DE PROXIMITÉ", title: "Recevoir les bons signaux au bon moment.", body: "Pour afficher les risques autour de vous, TravelGuard a besoin de votre position pendant l’utilisation. Vous pourrez gérer ce choix dans Réglages.", icon: "location.fill" as const, action: "Comprendre puis autoriser" },
];

const travelerOptions = ["Vacancier", "Backpacker", "Télétravailleur itinérant", "Voyageur fréquent"];
const priorityOptions = ["Menus gonflés", "Taxis abusifs", "Change douteux", "Billets non officiels"];

export default function OnboardingScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const [step, setStep] = useState(0);
  const [traveler, setTraveler] = useState("Vacancier");
  const [priorities, setPriorities] = useState<string[]>(["Menus gonflés", "Taxis abusifs"]);
  const current = steps[step];
  const progress = ((step + 1) / steps.length) * 100;
  const isChoiceStep = step === 1 || step === 2;
  const selectedCount = priorities.length;
  const detail = useMemo(() => step === 2 ? `${selectedCount} priorité${selectedCount > 1 ? "s" : ""} sélectionnée${selectedCount > 1 ? "s" : ""}` : step === 1 ? traveler : "Configuration personnalisée", [selectedCount, step, traveler]);

  function togglePriority(option: string) {
    setPriorities((currentValues) => currentValues.includes(option) ? currentValues.filter((value) => value !== option) : [...currentValues, option]);
  }

  async function finish() {
    await AsyncStorage.setItem("@travelguard/onboarding-complete", "true");
    router.replace("/(tabs)" as never);
  }

  async function requestLocationAndFinish() {
    if (Platform.OS === "web") {
      await finish();
      return;
    }
    const servicesEnabled = await Location.hasServicesEnabledAsync();
    if (!servicesEnabled) {
      Alert.alert("Activez la localisation", "TravelGuard a besoin du service de localisation pour afficher les risques autour de vous.", [{ text: "Plus tard", onPress: finish }, { text: "Réglages", onPress: () => { Linking.openSettings(); finish(); } }]);
      return;
    }
    const permission = await Location.requestForegroundPermissionsAsync();
    if (!permission.granted) {
      Alert.alert("Localisation non activée", "Vous pourrez réessayer depuis l’onglet Sécurité ou les réglages iOS.", [{ text: "Continuer", onPress: finish }, { text: "Ouvrir Réglages", onPress: () => { Linking.openSettings(); finish(); } }]);
      return;
    }
    await finish();
  }

  async function next() {
    if (step === steps.length - 1) return requestLocationAndFinish();
    setStep((value) => value + 1);
  }

  return (
    <ScreenContainer edges={["top", "left", "right", "bottom"]} containerClassName="bg-background">
      <View style={[styles.topBar, { paddingTop: Math.max(insets.top, 12) }]}><View style={[styles.logoMark, { backgroundColor: colors.primary }]}><Text style={styles.logoText}>TG</Text></View><Pressable onPress={finish} hitSlop={12}><Text style={[styles.skip, { color: colors.muted }]}>Passer</Text></Pressable></View>
      <View style={styles.progressTrack}><View style={[styles.progressFill, { width: `${progress}%`, backgroundColor: colors.primary }]} /></View>
      <ScrollView contentContainerStyle={[styles.scroll, { paddingBottom: Math.max(insets.bottom, 24) }]} showsVerticalScrollIndicator={false}>
        <View style={[styles.iconCircle, { backgroundColor: `${colors.primary}18` }]}><IconSymbol name={current.icon} size={39} color={colors.primary} /></View>
        <Text style={[styles.eyebrow, { color: colors.primary }]}>{current.eyebrow}</Text>
        <Text style={[styles.title, { color: colors.foreground }]}>{current.title}</Text>
        <Text style={[styles.body, { color: colors.muted }]}>{current.body}</Text>
        <Text style={[styles.stepCount, { color: colors.muted }]}>Étape {step + 1} sur {steps.length} · {detail}</Text>
        {isChoiceStep && <View style={styles.choices}>{(step === 1 ? travelerOptions : priorityOptions).map((option) => { const selected = step === 1 ? traveler === option : priorities.includes(option); return <Pressable key={option} onPress={() => step === 1 ? setTraveler(option) : togglePriority(option)} style={({ pressed }) => [styles.choice, { backgroundColor: selected ? `${colors.primary}14` : colors.surface, borderColor: selected ? colors.primary : colors.border }, pressed && { opacity: 0.75 }]}><View style={[styles.choiceIndicator, { borderColor: selected ? colors.primary : colors.border, backgroundColor: selected ? colors.primary : "transparent" }]}>{selected && <View style={styles.choiceDot} />}</View><Text style={[styles.choiceText, { color: colors.foreground }]}>{option}</Text><IconSymbol name="chevron.right" size={17} color={selected ? colors.primary : colors.muted} /></Pressable>; })}</View>}
        {!isChoiceStep && <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={[styles.detailBullet, { backgroundColor: colors.primary }]} /><View style={styles.detailCopy}><Text style={[styles.detailTitle, { color: colors.foreground }]}>{step === 6 ? "Pourquoi cette permission ?" : "Vous gardez le contrôle"}</Text><Text style={[styles.detailBody, { color: colors.muted }]}>{step === 6 ? "La carte peut fonctionner sans position précise, mais les alertes locales et la ville détectée sont plus utiles lorsque vous autorisez la localisation pendant l’utilisation." : "Aucune option n’est définitive. Les réglages, téléchargements et alertes restent modifiables depuis l’espace Sécurité."}</Text></View></View>}
      </ScrollView>
      <View style={[styles.bottomBar, { paddingBottom: Math.max(insets.bottom, 12), backgroundColor: colors.background }]}><Pressable onPress={next} style={({ pressed }) => [styles.primaryButton, { backgroundColor: colors.primary }, pressed && { opacity: 0.8, transform: [{ scale: 0.98 }] }]}><Text style={styles.primaryButtonText}>{current.action}</Text><IconSymbol name="chevron.right" size={19} color="#FFFFFF" /></Pressable>{step > 0 && <Pressable onPress={() => setStep((value) => value - 1)} hitSlop={10} style={styles.backButton}><Text style={[styles.backText, { color: colors.muted }]}>Retour</Text></Pressable>}</View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  topBar: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", paddingHorizontal: 20, paddingBottom: 15 },
  logoMark: { width: 38, height: 38, borderRadius: 13, alignItems: "center", justifyContent: "center" },
  logoText: { color: "#FFFFFF", fontWeight: "900", fontSize: 12 },
  skip: { fontSize: 13, fontWeight: "700" },
  progressTrack: { height: 4, marginHorizontal: 20, borderRadius: 4, backgroundColor: "#E3E7EA", overflow: "hidden" },
  progressFill: { height: 4, borderRadius: 4 },
  scroll: { padding: 24, paddingTop: 34 },
  iconCircle: { width: 82, height: 82, borderRadius: 28, alignItems: "center", justifyContent: "center", marginBottom: 28 },
  eyebrow: { fontSize: 11, fontWeight: "900", letterSpacing: 1.1 },
  title: { fontSize: 33, lineHeight: 39, fontWeight: "900", marginTop: 11, maxWidth: 340 },
  body: { fontSize: 16, lineHeight: 24, marginTop: 14, maxWidth: 350 },
  stepCount: { fontSize: 12, fontWeight: "700", marginTop: 20 },
  choices: { gap: 10, marginTop: 24 },
  choice: { minHeight: 58, borderRadius: 17, borderWidth: 1, paddingHorizontal: 14, flexDirection: "row", alignItems: "center", gap: 11 },
  choiceIndicator: { width: 22, height: 22, borderRadius: 11, borderWidth: 2, alignItems: "center", justifyContent: "center" },
  choiceDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: "#FFFFFF" },
  choiceText: { flex: 1, fontSize: 14, fontWeight: "800" },
  detailCard: { borderRadius: 19, borderWidth: 1, padding: 16, marginTop: 26, flexDirection: "row", gap: 11 },
  detailBullet: { width: 8, height: 8, borderRadius: 4, marginTop: 6 },
  detailCopy: { flex: 1 },
  detailTitle: { fontSize: 14, fontWeight: "800" },
  detailBody: { fontSize: 13, lineHeight: 19, marginTop: 5 },
  bottomBar: { paddingHorizontal: 20, paddingTop: 10, borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: "#E3E7EA" },
  primaryButton: { minHeight: 56, borderRadius: 18, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 10 },
  primaryButtonText: { color: "#FFFFFF", fontSize: 15, fontWeight: "900" },
  backButton: { alignItems: "center", paddingVertical: 10 },
  backText: { fontSize: 13, fontWeight: "700" },
});
