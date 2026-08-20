import { useRef, useState } from "react";
import { CameraView, useCameraPermissions } from "expo-camera";
import { Image, Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { useColors } from "@/hooks/use-colors";

type ScanType = "menu" | "bill" | "ticket";
const scanTypes: { key: ScanType; label: string }[] = [
  { key: "menu", label: "Menu" },
  { key: "bill", label: "Addition" },
  { key: "ticket", label: "Billet" },
];

export default function ScannerScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [scanType, setScanType] = useState<ScanType>("menu");
  const [photoUri, setPhotoUri] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function capture() {
    setError(null);
    if (Platform.OS === "web") {
      setError("La caméra et l’OCR de production sont disponibles dans l’application native Swift ouverte avec Xcode.");
      return;
    }
    if (!permission?.granted || !cameraRef.current) {
      setError(permission?.canAskAgain === false ? "La caméra est bloquée. Ouvrez Réglages pour autoriser TravelGuard." : "Autorisez la caméra avant de capturer un document.");
      return;
    }
    try {
      const photo = await cameraRef.current.takePictureAsync({ quality: 0.8, skipProcessing: false });
      if (!photo?.uri) throw new Error("missing-photo");
      setPhotoUri(photo.uri);
    } catch {
      setError("La photo n’a pas pu être capturée. Vérifiez la caméra et réessayez.");
    }
  }

  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <View style={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]}>
        <Text style={[styles.eyebrow, { color: colors.muted }]}>VÉRIFICATION AVANT PAIEMENT</Text>
        <Text style={[styles.title, { color: colors.foreground }]}>Scanner un document</Text>
        <Text style={[styles.copy, { color: colors.muted }]}>Le scanner OCR fiable est intégré au paquet Swift natif. Cet écran Expo ne fabrique aucun résultat et ne présente pas une capture comme un prix analysé.</Text>
        <View style={styles.typeRow}>{scanTypes.map((item) => <Pressable key={item.key} onPress={() => setScanType(item.key)} style={({ pressed }) => [styles.typeButton, { backgroundColor: scanType === item.key ? colors.primary : colors.surface, borderColor: scanType === item.key ? colors.primary : colors.border }, pressed && styles.pressed]}><Text style={{ color: scanType === item.key ? "#FFFFFF" : colors.foreground, fontWeight: "800" }}>{item.label}</Text></Pressable>)}</View>
        <View style={[styles.cameraCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          {Platform.OS !== "web" && permission?.granted ? <CameraView ref={cameraRef} style={styles.camera} facing="back" /> : <View style={styles.placeholder}><Text style={{ color: colors.foreground, fontWeight: "800" }}>{Platform.OS === "web" ? "Aperçu Expo non canonique" : permission?.canAskAgain === false ? "Caméra bloquée dans Réglages" : "Autorisation caméra requise"}</Text><Text style={{ color: colors.muted, textAlign: "center", marginTop: 8 }}>Ouvrez TravelGuard.xcodeproj pour utiliser Vision OCR sur iPhone.</Text></View>}
          {photoUri ? <Image source={{ uri: photoUri }} style={styles.preview} /> : null}
        </View>
        {!permission?.granted && Platform.OS !== "web" ? <Pressable onPress={requestPermission} style={[styles.action, { backgroundColor: colors.primary }]}><Text style={styles.actionText}>{permission?.canAskAgain === false ? "Ouvrir Réglages" : "Autoriser la caméra"}</Text></Pressable> : <Pressable onPress={capture} style={[styles.action, { backgroundColor: colors.primary }]}><Text style={styles.actionText}>{photoUri ? "Capturer à nouveau" : "Capturer la photo"}</Text></Pressable>}
        {photoUri ? <View style={[styles.notice, { backgroundColor: `${colors.warning}20`, borderColor: colors.warning }]}><Text style={{ color: colors.foreground, fontWeight: "800" }}>Photo capturée · analyse non effectuée dans Expo</Text><Text style={{ color: colors.muted, marginTop: 4 }}>Aucun prix, devise ou conclusion n’est déduit ici. Utilisez le scanner natif Swift pour l’OCR local.</Text></View> : null}
        {error ? <Text style={{ color: colors.error, marginTop: 12 }}>{error}</Text> : null}
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  content: { padding: 20, paddingTop: 18 },
  eyebrow: { fontSize: 10, fontWeight: "800", letterSpacing: 1.1 },
  title: { fontSize: 27, lineHeight: 34, fontWeight: "800", marginTop: 6 },
  copy: { fontSize: 14, lineHeight: 20, marginTop: 10 },
  typeRow: { flexDirection: "row", gap: 8, marginTop: 18, marginBottom: 14 },
  typeButton: { minHeight: 44, justifyContent: "center", paddingHorizontal: 15, borderRadius: 14, borderWidth: 1 },
  cameraCard: { height: 360, borderRadius: 24, overflow: "hidden", borderWidth: 1, position: "relative" },
  camera: { flex: 1 },
  placeholder: { flex: 1, alignItems: "center", justifyContent: "center", padding: 32 },
  preview: { ...StyleSheet.absoluteFillObject, resizeMode: "contain", backgroundColor: "#000" },
  action: { minHeight: 56, borderRadius: 18, marginTop: 16, alignItems: "center", justifyContent: "center" },
  actionText: { color: "#FFFFFF", fontSize: 15, fontWeight: "800" },
  notice: { borderWidth: 1, borderRadius: 16, padding: 14, marginTop: 14 },
  pressed: { opacity: 0.75 },
});
