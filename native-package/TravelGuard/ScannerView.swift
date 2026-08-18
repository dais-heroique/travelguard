import PhotosUI
import SwiftUI
import UIKit
import Vision

struct ScannerView: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var recognizedText = ""
    @State private var isAnalyzing = false
    @State private var showingCamera = false
    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 18) { Text("CONTRÔLE INTELLIGENT").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Scanner avant de payer").font(.largeTitle.bold()); Text("Cadrez un menu, une addition ou un billet. L’analyse locale extrait les textes lisibles et vous aide à repérer ce qui mérite vérification.").foregroundStyle(TGColor.muted)
            Button { showingCamera = true } label: { Label("Prendre une photo", systemImage: "camera.fill").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)) }
            PhotosPicker(selection: $selectedItem, matching: .images) { Label("Choisir une photo", systemImage: "photo").font(.headline).foregroundStyle(TGColor.ink).frame(maxWidth: .infinity).padding().background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) }.onChange(of: selectedItem) { _, item in Task { await analyze(item) } }
            if isAnalyzing { ProgressView("Analyse du texte…").padding(.vertical) }
            if !recognizedText.isEmpty { VStack(alignment: .leading, spacing: 10) { Text("Texte détecté").font(.headline); Text(recognizedText).font(.body).foregroundStyle(TGColor.muted) }.tgCard() }
            Text("Hors connexion : la capture et l’extraction du texte restent disponibles. Une comparaison avec des données distantes nécessitera une connexion.").font(.footnote).foregroundStyle(TGColor.muted).padding(.top, 8)
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).sheet(isPresented: $showingCamera) { CameraPicker { image in Task { await recognize(image) } } } }
    }
    private func analyze(_ item: PhotosPickerItem?) async { guard let item, let data = try? await item.loadTransferable(type: Data.self), let image = UIImage(data: data) else { return }; await recognize(image) }
    @MainActor private func recognize(_ image: UIImage) async { guard let cgImage = image.cgImage else { return }; isAnalyzing = true; let request = VNRecognizeTextRequest { request, _ in let observations = request.results as? [VNRecognizedTextObservation] ?? []; let text = observations.compactMap { $0.topCandidates(1).first?.string }.joined(separator: "\n"); Task { @MainActor in self.recognizedText = text; self.isAnalyzing = false } }; request.recognitionLevel = .accurate; request.recognitionLanguages = ["fr-FR", "en-US"]; try? VNImageRequestHandler(cgImage: cgImage).perform([request]) }
}

struct CameraPicker: UIViewControllerRepresentable { let onImage: (UIImage) -> Void; func makeCoordinator() -> Coordinator { Coordinator(onImage: onImage) }; func makeUIViewController(context: Context) -> UIImagePickerController { let picker = UIImagePickerController(); picker.sourceType = .camera; picker.delegate = context.coordinator; return picker }; func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}; final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate { let onImage: (UIImage) -> Void; init(onImage: @escaping (UIImage) -> Void) { self.onImage = onImage }; func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) { if let image = info[.originalImage] as? UIImage { onImage(image) }; picker.dismiss(animated: true) }; func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { picker.dismiss(animated: true) } } }
