import CoreImage
import Foundation
import PhotosUI
import SwiftUI
import UIKit
import Vision

struct OCRSummary {
    var currency = ""
    var subtotal: Double?
    var tax: Double?
    var service: Double?
    var total: Double?
    var amounts: [Double] = []
    var hasData: Bool { !amounts.isEmpty || subtotal != nil || tax != nil || service != nil || total != nil }
}

struct ScannerView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var selectedItem: PhotosPickerItem?
    @State private var recognizedLines: [String] = []
    @State private var suspectLines: Set<String> = []
    @State private var summary = OCRSummary()
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
                    if summary.hasData { VStack(alignment: .leading, spacing: 6) { Text("Lecture structurée").font(.subheadline.bold()); if let subtotal = summary.subtotal { Text("Sous-total : \(subtotal, specifier: \"%.2f\") \(summary.currency)") }; if let tax = summary.tax { Text("Taxes : \(tax, specifier: \"%.2f\") \(summary.currency)") }; if let service = summary.service { Text("Service : \(service, specifier: \"%.2f\") \(summary.currency)") }; if let total = summary.total { Text("Total détecté : \(total, specifier: \"%.2f\") \(summary.currency)").fontWeight(.bold) }; Text("Cette lecture est indicative : vérifiez toujours le document original.").font(.caption).foregroundStyle(TGColor.muted) }.padding(.top, 8) }
                }.tgCard()
            } else if !isAnalyzing {
                VStack(alignment: .leading, spacing: 8) { Label("Aucun document analysé", systemImage: "viewfinder").font(.headline); Text("Prenez une photo ou choisissez une image pour lancer la détection du texte.").font(.subheadline).foregroundStyle(TGColor.muted) }.tgCard()
            }
            Label(store.network.isChecking ? "Vérification du réseau…" : store.network.isOnline ? "En ligne · OCR local disponible" : "Hors ligne · OCR local disponible", systemImage: store.network.isOnline ? "wifi" : "wifi.slash").font(.footnote).foregroundStyle(TGColor.muted).padding(.top, 8)
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).sheet(isPresented: $showingCamera) { CameraPicker { image in Task { await recognize(image) } } } }
    }
    @MainActor private func analyze(_ item: PhotosPickerItem?) async {
        guard let item else { return }
        defer { selectedItem = nil }
        do {
            guard let data = try await item.loadTransferable(type: Data.self), let image = UIImage(data: data) else { recognizedLines = ["Image impossible à charger. Choisissez une autre photo et réessayez."]; return }
            await recognize(image)
        } catch {
            recognizedLines = ["La photo n’a pas pu être lue. Choisissez une autre image et réessayez."]
        }
        return
    }
    @MainActor private func recognize(_ image: UIImage) async {
        let prepared = prepareImage(image)
        guard let cgImage = prepared.cgImage else { recognizedLines = ["Format d’image non pris en charge."]; isAnalyzing = false; return }
        isAnalyzing = true; recognizedLines = []; suspectLines = []; summary = OCRSummary()
        let request = VNRecognizeTextRequest { request, _ in
            let observations = request.results as? [VNRecognizedTextObservation] ?? []
            let lines = observations.compactMap { $0.topCandidates(1).first?.string }.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
            let suspects = Set(lines.filter { line in let lower = line.lowercased(); return ["service", "frais", "commission", "taxe", "tax", "tip", "extra", "suppl", "tourist", "cash"].contains { lower.contains($0) } })
            let parsed = parse(lines)
            Task { @MainActor in self.recognizedLines = lines.isEmpty ? ["Aucun texte lisible détecté. Rapprochez le document, améliorez la lumière et réessayez."] : lines; self.suspectLines = suspects; self.summary = parsed; self.isAnalyzing = false }
        }
        request.recognitionLevel = .accurate
        let desiredLanguages = ["fr-FR", "en-US", "it-IT", "es-ES", "de-DE", "pt-PT", "sl-SI", "hr-HR"]
        if let supported = try? VNRecognizeTextRequest.supportedRecognitionLanguages(for: .accurate, revision: VNRecognizeTextRequest.currentRevision) { request.recognitionLanguages = desiredLanguages.filter { supported.contains($0) } }
        do { try VNImageRequestHandler(cgImage: cgImage).perform([request]) } catch { recognizedLines = ["L’analyse a échoué. Vérifiez la lumière et réessayez."]; isAnalyzing = false }
    }

    private func prepareImage(_ image: UIImage) -> UIImage {
        let renderer = UIGraphicsImageRenderer(size: image.size)
        let normalized = renderer.image { _ in image.draw(in: CGRect(origin: .zero, size: image.size)) }
        guard let input = CIImage(image: normalized), let filter = CIFilter(name: "CIColorControls") else { return normalized }
        filter.setValue(input, forKey: kCIInputImageKey); filter.setValue(1.15, forKey: kCIInputContrastKey); filter.setValue(0.05, forKey: kCIInputBrightnessKey)
        guard let output = filter.outputImage, let cg = CIContext().createCGImage(output, from: output.extent) else { return normalized }
        return UIImage(cgImage: cg, scale: normalized.scale, orientation: .up)
    }

    private func parse(_ lines: [String]) -> OCRSummary {
        var result = OCRSummary()
        let regex = try? NSRegularExpression(pattern: "(?<![0-9])([0-9]{1,4}(?:[.,][0-9]{1,2})?)\\s*(€|EUR|USD|\\$|£|GBP|CHF)?", options: .caseInsensitive)
        for line in lines {
            let lower = line.lowercased()
            let matches = regex?.matches(in: line, range: NSRange(line.startIndex..., in: line)) ?? []
            let values = matches.compactMap { match -> Double? in
                guard let range = Range(match.range(at: 1), in: line) else { return nil }
                return Double(line[range].replacingOccurrences(of: ",", with: "."))
            }
            if let symbolRange = matches.first.flatMap({ Range($0.range(at: 2), in: line) }) { result.currency = String(line[symbolRange]) }
            guard let value = values.last else { continue }
            result.amounts.append(value)
            if lower.contains("total") || lower.contains("amount due") || lower.contains("à payer") || lower.contains("a payer") { result.total = value }
            else if lower.contains("tax") || lower.contains("tva") || lower.contains("vat") { result.tax = value }
            else if lower.contains("service") || lower.contains("tip") { result.service = value }
            else if result.subtotal == nil { result.subtotal = value }
        }
        return result
    }
}

struct CameraPicker: UIViewControllerRepresentable { let onImage: (UIImage) -> Void; func makeCoordinator() -> Coordinator { Coordinator(onImage: onImage) }; func makeUIViewController(context: Context) -> UIImagePickerController { let picker = UIImagePickerController(); picker.sourceType = .camera; picker.delegate = context.coordinator; return picker }; func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}; final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate { let onImage: (UIImage) -> Void; init(onImage: @escaping (UIImage) -> Void) { self.onImage = onImage }; func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) { if let image = info[.originalImage] as? UIImage { onImage(image) }; picker.dismiss(animated: true) }; func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { picker.dismiss(animated: true) } } }
