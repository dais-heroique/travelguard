import PhotosUI
import SwiftUI
import UIKit
import Vision

struct ScannerView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var selectedItem: PhotosPickerItem?
    @State private var recognizedText = ""
    @State private var recognizedLines: [String] = []
    @State private var suspectLines: Set<String> = []
    @State private var isAnalyzing = false
    @State private var showingCamera = false
    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 18) {
            Text("CONTRÔLE INTELLIGENT").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted)
            Text("Scanner avant de payer").font(.largeTitle.bold())
            Text("Cadrez un menu, une addition ou un billet. Les lignes qui méritent une vérification apparaissent en rouge.").foregroundStyle(TGColor.muted)
            Button { showingCamera = true } label: { Label("Prendre une photo", systemImage: "camera.fill").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)) }
            PhotosPicker(selection: $selectedItem, matching: .images) { Label("Choisir une photo", systemImage: "photo").font(.headline).foregroundStyle(TGColor.ink).frame(maxWidth: .infinity).padding().background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) }.onChange(of: selectedItem) { _, item in Task { await analyze(item) } }
            if isAnalyzing { ProgressView("Analyse locale du document…").padding(.vertical) }
            if !recognizedLines.isEmpty {
                VStack(alignment: .leading, spacing: 10) {
                    Label("Résultat du contrôle", systemImage: suspectLines.isEmpty ? "checkmark.circle.fill" : "exclamationmark.triangle.fill").font(.headline).foregroundStyle(suspectLines.isEmpty ? .green : TGColor.coral)
                    ForEach(recognizedLines, id: \.self) { line in
                        Text(line).font(.body.weight(suspectLines.contains(line) ? .semibold : .regular)).foregroundStyle(suspectLines.contains(line) ? .red : TGColor.ink).padding(.vertical, 3)
                    }
                    if !suspectLines.isEmpty { Text("Vérifiez ces lignes avant de payer : frais, service, commission ou supplément peuvent être ajoutés.").font(.footnote).foregroundStyle(.red) }
                }.tgCard()
            } else if !isAnalyzing {
                VStack(alignment: .leading, spacing: 8) { Label("Aucun document analysé", systemImage: "viewfinder").font(.headline); Text("Prenez une photo ou choisissez une image pour lancer la détection du texte.").font(.subheadline).foregroundStyle(TGColor.muted) }.tgCard()
            }
            Label(store.network.isChecking ? "Vérification du réseau…" : store.network.isOnline ? "En ligne · OCR local disponible" : "Hors ligne · OCR local disponible", systemImage: store.network.isOnline ? "wifi" : "wifi.slash").font(.footnote).foregroundStyle(TGColor.muted).padding(.top, 8)
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).sheet(isPresented: $showingCamera) { CameraPicker { image in Task { await recognize(image) } } } }
    }
    @MainActor private func analyze(_ item: PhotosPickerItem?) async {
        guard let item else { return }
        do {
            guard let data = try await item.loadTransferable(type: Data.self), let image = UIImage(data: data) else { recognizedLines = ["Image impossible à charger. Choisissez une autre photo et réessayez."]; return }
            await recognize(image)
        } catch {
            recognizedLines = ["La photo n’a pas pu être lue. Choisissez une autre image et réessayez."]
        }
        return
    }
    @MainActor private func recognize(_ image: UIImage) async {
        guard let cgImage = image.cgImage else { recognizedLines = ["Format d’image non pris en charge."]; isAnalyzing = false; return }
        isAnalyzing = true; recognizedLines = []; suspectLines = []
        let request = VNRecognizeTextRequest { request, _ in
            let observations = request.results as? [VNRecognizedTextObservation] ?? []
            let lines = observations.compactMap { $0.topCandidates(1).first?.string }.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
            let suspects = Set(lines.filter { line in let lower = line.lowercased(); return ["service", "frais", "commission", "taxe", "tax", "tip", "extra", "suppl", "tourist", "cash"].contains { lower.contains($0) } })
            Task { @MainActor in self.recognizedLines = lines.isEmpty ? ["Aucun texte lisible détecté. Rapprochez le document, améliorez la lumière et réessayez."] : lines; self.recognizedText = lines.joined(separator: "\n"); self.suspectLines = suspects; self.isAnalyzing = false }
        }
        request.recognitionLevel = .accurate; request.recognitionLanguages = ["fr-FR", "en-US"]
        do { try VNImageRequestHandler(cgImage: cgImage).perform([request]) } catch { recognizedLines = ["L’analyse a échoué. Vérifiez la lumière et réessayez."]; isAnalyzing = false }
    }
}

struct CameraPicker: UIViewControllerRepresentable { let onImage: (UIImage) -> Void; func makeCoordinator() -> Coordinator { Coordinator(onImage: onImage) }; func makeUIViewController(context: Context) -> UIImagePickerController { let picker = UIImagePickerController(); picker.sourceType = .camera; picker.delegate = context.coordinator; return picker }; func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}; final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate { let onImage: (UIImage) -> Void; init(onImage: @escaping (UIImage) -> Void) { self.onImage = onImage }; func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) { if let image = info[.originalImage] as? UIImage { onImage(image) }; picker.dismiss(animated: true) }; func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { picker.dismiss(animated: true) } } }
