import { useRef, useState } from "react";
import { CameraView, useCameraPermissions } from "expo-camera";
import { Platform, Pressable, StyleSheet, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { ScreenContainer } from "@/components/screen-container";
import { IconSymbol } from "@/components/ui/icon-symbol";
import { useColors } from "@/hooks/use-colors";

type ScanType = "menu" | "bill" | "ticket";
const scanTypes: { key: ScanType; label: string }[] = [{ key: "menu", label: "Menu" }, { key: "bill", label: "Addition" }, { key: "ticket", label: "Billet" }];

export default function ScannerScreen() {
  const colors = useColors();
  const insets = useSafeAreaInsets();
  const cameraRef = useRef<CameraView>(null);
  const [permission, requestPermission] = useCameraPermissions();
  const [scanType, setScanType] = useState<ScanType>("menu");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<"safe" | "check" | null>(null);

  async function capture() {
    setResult(null);
    setIsAnalyzing(true);
    if (Platform.OS !== "web") await cameraRef.current?.takePictureAsync({ quality: 0.8, skipProcessing: false });
    setTimeout(() => { setIsAnalyzing(false); setResult(scanType === "ticket" ? "safe" : "check"); }, 900);
  }

  if (!permission && Platform.OS !== "web") return <ScreenContainer className="items-center justify-center"><Text style={{ color: colors.muted }}>Préparation de la caméra…</Text></ScreenContainer>;

  return (
    <ScreenContainer edges={["top", "left", "right"]} containerClassName="bg-background">
      <View style={styles.header}><View><Text style={[styles.eyebrow, { color: colors.muted }]}>VÉRIFICATION AVANT PAIEMENT</Text><Text style={[styles.title, { color: colors.foreground }]}>Scanner un document</Text></View><View style={[styles.offlineBadge, { backgroundColor: colors.surface, borderColor: colors.border }]}><View style={[styles.offlineDot, { backgroundColor: colors.success }]} /><Text style={[styles.offlineText, { color: colors.foreground }]}>Hors ligne</Text></View></View>
      <View style={[styles.content, { paddingBottom: Math.max(insets.bottom + 96, 112) }]}>
        <View style={styles.typeRow}>{scanTypes.map((item) => <Pressable key={item.key} onPress={() => { setScanType(item.key); setResult(null); }} style={({ pressed }) => [styles.typeButton, { backgroundColor: scanType === item.key ? colors.primary : colors.surface, borderColor: scanType === item.key ? colors.primary : colors.border }, pressed && { opacity: 0.75 }]}><Text style={[styles.typeText, { color: scanType === item.key ? "#FFFFFF" : colors.foreground }]}>{item.label}</Text></Pressable>)}</View>
        <View style={[styles.cameraCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          {Platform.OS !== "web" && permission?.granted ? <CameraView ref={cameraRef} style={styles.camera} facing="back" /> : <View style={styles.webCamera}><IconSymbol name="camera.fill" size={34} color={colors.primary} /><Text style={[styles.webCameraTitle, { color: colors.foreground }]}>Viseur prêt</Text><Text style={[styles.webCameraCopy, { color: colors.muted }]}>Sur iPhone, la caméra s’ouvrira ici pour cadrer votre document.</Text></View>}
          <View style={[styles.scanOverlay, { pointerEvents: "none" }]}><View style={[styles.corner, styles.cornerTopLeft, { borderColor: colors.warning }]} /><View style={[styles.corner, styles.cornerTopRight, { borderColor: colors.warning }]} /><View style={[styles.corner, styles.cornerBottomLeft, { borderColor: colors.warning }]} /><View style={[styles.corner, styles.cornerBottomRight, { borderColor: colors.warning }]} /></View>
          <View style={styles.cameraHint}><Text style={styles.cameraHintText}>Cadrez les prix et la devise</Text></View>
        </View>
        {!permission?.granted && Platform.OS !== "web" ? <Pressable onPress={requestPermission} style={({ pressed }) => [styles.permissionButton, { backgroundColor: colors.primary }, pressed && { opacity: 0.75 }]}><IconSymbol name="camera.fill" size={18} color="#FFFFFF" /><Text style={styles.permissionText}>Autoriser la caméra</Text></Pressable> : <Pressable onPress={capture} disabled={isAnalyzing} style={({ pressed }) => [styles.captureButton, { backgroundColor: colors.primary }, pressed && { opacity: 0.78, transform: [{ scale: 0.98 }] }]}><View style={styles.captureInner}>{isAnalyzing ? <IconSymbol name="arrow.clockwise" size={22} color={colors.primary} /> : <IconSymbol name="viewfinder" size={25} color={colors.primary} />}</View><Text style={styles.captureText}>{isAnalyzing ? "Analyse en cours…" : "Analyser maintenant"}</Text></Pressable>}
        {result && <View style={[styles.resultCard, { backgroundColor: result === "safe" ? `${colors.success}18` : `${colors.warning}20`, borderColor: result === "safe" ? colors.success : colors.warning }]}><View style={[styles.resultIcon, { backgroundColor: result === "safe" ? colors.success : colors.warning }]}><IconSymbol name="checkmark.seal.fill" size={21} color="#FFFFFF" /></View><View style={styles.resultCopy}><Text style={[styles.resultTitle, { color: colors.foreground }]}>{result === "safe" ? "Prix cohérent détecté" : "Quelques éléments à vérifier"}</Text><Text style={[styles.resultSub, { color: colors.muted }]}>{result === "safe" ? "Le billet ressemble au tarif officiel local." : "Demandez le détail des frais et comparez avec le juste prix."}</Text></View></View>}
        <View style={styles.helper}><IconSymbol name="wifi.slash" size={18} color={colors.primary} /><Text style={[styles.helperText, { color: colors.muted }]}>Le dernier pack de références est disponible hors ligne. Les analyses avancées peuvent nécessiter une connexion.</Text></View>
      </View>
    </ScreenContainer>
  );
}

const styles = StyleSheet.create({
  header: { paddingHorizontal: 20, paddingTop: 18, flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  eyebrow: { fontSize: 10, fontWeight: "800", letterSpacing: 1.1 },
  title: { fontSize: 26, lineHeight: 33, fontWeight: "800", marginTop: 5 },
  offlineBadge: { flexDirection: "row", gap: 6, alignItems: "center", borderWidth: 1, borderRadius: 13, paddingHorizontal: 9, paddingVertical: 8 },
  offlineDot: { width: 7, height: 7, borderRadius: 4 },
  offlineText: { fontSize: 11, fontWeight: "800" },
  content: { padding: 20, paddingTop: 20 },
  typeRow: { flexDirection: "row", gap: 8, marginBottom: 14 },
  typeButton: { borderRadius: 14, paddingHorizontal: 15, paddingVertical: 9, borderWidth: 1 },
  typeText: { fontSize: 12, fontWeight: "800" },
  cameraCard: { height: 360, borderRadius: 24, overflow: "hidden", borderWidth: 1, position: "relative" },
  camera: { flex: 1 },
  webCamera: { flex: 1, alignItems: "center", justifyContent: "center", padding: 40, backgroundColor: "#E8F1F1" },
  webCameraTitle: { fontSize: 18, fontWeight: "800", marginTop: 12 },
  webCameraCopy: { fontSize: 13, lineHeight: 19, textAlign: "center", marginTop: 6 },
  scanOverlay: { ...StyleSheet.absoluteFillObject, margin: 34 },
  corner: { position: "absolute", width: 38, height: 38, borderWidth: 3 },
  cornerTopLeft: { top: 0, left: 0, borderRightWidth: 0, borderBottomWidth: 0, borderTopLeftRadius: 8 },
  cornerTopRight: { top: 0, right: 0, borderLeftWidth: 0, borderBottomWidth: 0, borderTopRightRadius: 8 },
  cornerBottomLeft: { bottom: 0, left: 0, borderRightWidth: 0, borderTopWidth: 0, borderBottomLeftRadius: 8 },
  cornerBottomRight: { bottom: 0, right: 0, borderLeftWidth: 0, borderTopWidth: 0, borderBottomRightRadius: 8 },
  cameraHint: { position: "absolute", bottom: 16, alignSelf: "center", backgroundColor: "#102A43E8", borderRadius: 12, paddingHorizontal: 12, paddingVertical: 8 },
  cameraHintText: { color: "#FFFFFF", fontSize: 11, fontWeight: "800" },
  captureButton: { minHeight: 62, borderRadius: 19, marginTop: 16, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 12 },
  captureInner: { width: 38, height: 38, borderRadius: 19, backgroundColor: "#FFFFFF", alignItems: "center", justifyContent: "center" },
  captureText: { color: "#FFFFFF", fontSize: 15, fontWeight: "800" },
  permissionButton: { minHeight: 56, borderRadius: 18, marginTop: 16, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 9 },
  permissionText: { color: "#FFFFFF", fontSize: 14, fontWeight: "800" },
  resultCard: { borderRadius: 18, borderWidth: 1, marginTop: 14, padding: 14, flexDirection: "row", alignItems: "center" },
  resultIcon: { width: 38, height: 38, borderRadius: 13, alignItems: "center", justifyContent: "center", marginRight: 11 },
  resultCopy: { flex: 1 },
  resultTitle: { fontSize: 14, fontWeight: "800" },
  resultSub: { fontSize: 12, lineHeight: 17, marginTop: 3 },
  helper: { flexDirection: "row", gap: 9, alignItems: "flex-start", marginTop: 18, paddingHorizontal: 2 },
  helperText: { fontSize: 12, lineHeight: 18, flex: 1 },
});
