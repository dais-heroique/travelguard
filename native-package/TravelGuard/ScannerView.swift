import CoreImage
import Foundation
import PhotosUI
import SwiftUI
import UIKit
import Vision

enum OCRSupport {
    static let amountPattern = #"(?:(EUR|USD|CHF|GBP|JPY|CZK|PLN|HUF|SEK|NOK|DKK|AED|THB|VND|KRW|MAD|TRY|INR|AUD|NZD|CAD|€|\$|£|¥|₩|د\.إ|฿|₫|₺)\s*)?([0-9]{1,3}(?:[ .\u{00A0}']\s?[0-9]{3})*(?:[.,][0-9]{1,2})?|[0-9]+(?:[.,][0-9]{1,2})?)\s*(EUR|USD|CHF|GBP|JPY|CZK|PLN|HUF|SEK|NOK|DKK|AED|THB|VND|KRW|MAD|TRY|INR|AUD|NZD|CAD|€|\$|£|¥|₩|د\.إ|฿|₫|₺)?"#
    static let labelPattern = #"\b(total|subtotal|sous[- ]?total|amount due|à payer|a payer|taxe?|tva|vat|service|tip|service charge|frais|commission|surcharge|supplement)\b"#

    static func normalizeNumber(_ raw: String) -> Double? {
        var value = raw.replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "\u{00A0}", with: "")
        let comma = value.lastIndex(of: ",")
        let dot = value.lastIndex(of: ".")
        if let comma, let dot {
            if comma > dot { value = value.replacingOccurrences(of: ".", with: "").replacingOccurrences(of: ",", with: ".") }
            else { value = value.replacingOccurrences(of: ",", with: "") }
        } else if value.contains(",") {
            let parts = value.split(separator: ",")
            value = parts.count == 2 && parts[1].count <= 2 ? value.replacingOccurrences(of: ",", with: ".") : value.replacingOccurrences(of: ",", with: "")
        } else if value.contains(".") {
            let parts = value.split(separator: ".")
            if parts.count == 2 && parts[1].count == 3 && parts[0].count <= 3 { value = value.replacingOccurrences(of: ".", with: "") }
        }
        return Double(value)
    }

    static func currency(for countryCode: String) -> String {
        switch countryCode.uppercased() { case "US": return "USD"; case "CA": return "CAD"; case "GB": return "GBP"; case "CH": return "CHF"; case "JP": return "JPY"; case "CZ": return "CZK"; case "PL": return "PLN"; case "HU": return "HUF"; case "SE": return "SEK"; case "NO": return "NOK"; case "DK": return "DKK"; case "AE": return "AED"; case "TH": return "THB"; case "VN": return "VND"; case "KR": return "KRW"; case "MA": return "MAD"; case "TR": return "TRY"; case "IN": return "INR"; case "AU": return "AUD"; case "NZ": return "NZD"; case "FR", "DE", "ES", "IT", "PT", "BE", "NL", "IE", "AT", "FI", "GR": return "EUR"; default: return "INCONNUE" }
    }

    static func parse(_ lines: [String], fallbackCurrency: String) -> OCRSummary {
        var result = OCRSummary(); result.currency = fallbackCurrency
        let regex = try? NSRegularExpression(pattern: amountPattern, options: .caseInsensitive)
        for line in lines {
            let lower = line.lowercased()
            if lower.range(of: #"\\b[0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}\\b"#, options: .regularExpression) != nil { continue }
            let matches = regex?.matches(in: line, range: NSRange(line.startIndex..., in: line)) ?? []
            for match in matches {
                guard let numberRange = Range(match.range(at: 2), in: line), let value = normalizeNumber(String(line[numberRange])) else { continue }
                let prefix = Range(match.range(at: 1), in: line).map { String(line[$0]) } ?? ""
                let suffix = Range(match.range(at: 3), in: line).map { String(line[$0]) } ?? ""
                let detectedCurrency = !prefix.isEmpty ? prefix : suffix
                if !detectedCurrency.isEmpty { result.currency = detectedCurrency }
                result.amounts.append(value)
                let isTotal = lower.range(of: #"\\b(total|amount due|à payer|a payer)\\b"#, options: .regularExpression) != nil
                let isSubtotal = lower.range(of: #"\\b(subtotal|sous[- ]?total)\\b"#, options: .regularExpression) != nil
                let isTax = lower.range(of: #"\\b(taxe?|tva|vat)\\b"#, options: .regularExpression) != nil
                let isService = lower.range(of: #"\\b(service|tip|service charge|frais|commission|surcharge|supplement)\\b"#, options: .regularExpression) != nil
                if isTotal { result.total = value } else if isSubtotal { result.subtotal = value } else if isTax { result.tax = value } else if isService { result.service = value } else { result.itemAmounts.append(value) }
            }
        }
        return result
    }
}

enum OCRAssessment: Equatable {
    case coherent, unusual, abusive, undetermined
    var title: String { switch self { case .coherent: return "Prix cohérent"; case .unusual: return "Prix inhabituel"; case .abusive: return "Prix probablement abusif"; case .undetermined: return "Impossible à déterminer" } }
    var icon: String { switch self { case .coherent: return "checkmark.circle.fill"; case .unusual: return "exclamationmark.triangle.fill"; case .abusive: return "xmark.octagon.fill"; case .undetermined: return "questionmark.circle.fill" } }
}

struct OCRSummary: Sendable {
    var currency = ""
    var subtotal: Double?
    var tax: Double?
    var service: Double?
    var total: Double?
    var amounts: [Double] = []
    var itemAmounts: [Double] = []
    var calculatedTotal: Double? {
        let base: Double?
        if itemAmounts.isEmpty { base = subtotal } else { base = itemAmounts.reduce(0, +) }
        guard let base else { return nil }
        return base + (tax ?? 0) + (service ?? 0)
    }
    var difference: Double? { guard let total, let calculatedTotal else { return nil }; return total - calculatedTotal }
    var hasData: Bool { !amounts.isEmpty || subtotal != nil || tax != nil || service != nil || total != nil }
    func assessment(suspectLines: Set<String>) -> OCRAssessment {
        guard hasData else { return .undetermined }
        if let difference, abs(difference) > 0.05 { return .unusual }
        guard total != nil || subtotal != nil || !itemAmounts.isEmpty else { return .undetermined }
        return .coherent
    }
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
            Text("Cadrez un menu, une addition ou un billet. L’analyse est locale et indicative : aucune conclusion officielle n’est inventée.").foregroundStyle(TGColor.muted)
            Button { showingCamera = true } label: { Label("Prendre une photo", systemImage: "camera.fill").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)) }
            PhotosPicker(selection: $selectedItem, matching: .images) { Label("Choisir une photo", systemImage: "photo").font(.headline).foregroundStyle(TGColor.ink).frame(maxWidth: .infinity).padding().background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) }.onChange(of: selectedItem) { _, item in Task { await analyze(item) } }
            if isAnalyzing { ProgressView("Analyse locale du document…").padding(.vertical) }
            if !recognizedLines.isEmpty { VStack(alignment: .leading, spacing: 10) {
                let assessment = summary.assessment(suspectLines: suspectLines)
                Label(assessment.title, systemImage: assessment.icon).font(.headline).foregroundStyle(assessment == .coherent ? .green : assessment == .abusive ? .red : assessment == .unusual ? TGColor.amber : TGColor.muted)
                ForEach(recognizedLines, id: \.self) { line in Text(line).font(.body.weight(suspectLines.contains(line) ? .semibold : .regular)).foregroundStyle(suspectLines.contains(line) ? .red : TGColor.ink).padding(.vertical, 3) }
                if !suspectLines.isEmpty { Text("Vérifiez les frais, taxes, commissions et suppléments avant de payer.").font(.footnote).foregroundStyle(.red) }
                if summary.hasData { VStack(alignment: .leading, spacing: 6) { Text("Lecture structurée").font(.subheadline.bold()); if !summary.itemAmounts.isEmpty { Text("Articles détectés : \(summary.itemAmounts.reduce(0, +), specifier: \"%.2f\") \(summary.currency)") }; if let subtotal = summary.subtotal { Text("Sous-total indiqué : \(subtotal, specifier: \"%.2f\") \(summary.currency)") }; if let tax = summary.tax { Text("Taxes : \(tax, specifier: \"%.2f\") \(summary.currency)") }; if let service = summary.service { Text("Service : \(service, specifier: \"%.2f\") \(summary.currency)") }; if let total = summary.total { Text("Total détecté : \(total, specifier: \"%.2f\") \(summary.currency)").fontWeight(.bold) }; if let calculated = summary.calculatedTotal, let difference = summary.difference { Text(abs(difference) <= 0.05 ? "Total cohérent avec les lignes détectées : \(calculated, specifier: \"%.2f\") \(summary.currency)" : "Écart arithmétique à vérifier : \(difference, specifier: \"%.2f\") \(summary.currency)").foregroundStyle(abs(difference) <= 0.05 ? .green : .red).font(.footnote.bold()) }; Text("Résultat limité au document : le total peut être mathématiquement cohérent sans être un prix juste. Aucune comparaison FairPrice officielle n’est disponible sans source locale autorisée.").font(.caption).foregroundStyle(TGColor.muted) }.padding(.top, 8) }
            }.tgCard() } else if !isAnalyzing { VStack(alignment: .leading, spacing: 8) { Label("Aucun document analysé", systemImage: "viewfinder").font(.headline); Text("Prenez une photo ou choisissez une image pour lancer la détection du texte.").font(.subheadline).foregroundStyle(TGColor.muted) }.tgCard() }
            Label(store.network.isChecking ? "Vérification du réseau…" : store.network.isOnline ? "En ligne · OCR local disponible" : "Hors ligne · OCR local disponible", systemImage: store.network.isOnline ? "wifi" : "wifi.slash").font(.footnote).foregroundStyle(TGColor.muted).padding(.top, 8)
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).sheet(isPresented: $showingCamera) { CameraPicker { image in Task { await recognize(image) } } } }
    }
    @MainActor private func analyze(_ item: PhotosPickerItem?) async { guard let item else { return }; defer { selectedItem = nil }; do { guard let data = try await item.loadTransferable(type: Data.self), let image = UIImage(data: data) else { recognizedLines = ["Image impossible à charger."]; return }; await recognize(image) } catch { recognizedLines = ["La photo n’a pas pu être lue. Choisissez une autre image et réessayez."] } }
    @MainActor private func recognize(_ image: UIImage) async {
        guard let prepared = OCRSupport.prepareImage(image), let cgImage = prepared.cgImage else { recognizedLines = ["Format d’image non pris en charge."]; return }
        isAnalyzing = true; recognizedLines = []; suspectLines = []; summary = OCRSummary()
        let languages = ["fr-FR", "en-US", "it-IT", "es-ES", "de-DE", "pt-PT", "sl-SI", "hr-HR"]
        let supported = (try? VNRecognizeTextRequest.supportedRecognitionLanguages(for: .accurate, revision: VNRecognizeTextRequest.currentRevision)) ?? []
        let selectedLanguages = languages.filter { supported.contains($0) }
        let fallbackCurrency = OCRSupport.currency(for: store.location.countryCode)
        let result = await Task.detached(priority: .userInitiated) { () -> (lines: [String], summary: OCRSummary) in
            var outputLines: [String] = []; var requestSummary = OCRSummary(); let semaphore = DispatchSemaphore(value: 0)
            let request = VNRecognizeTextRequest { request, _ in
                let observations = request.results as? [VNRecognizedTextObservation] ?? []
                outputLines = observations.compactMap { $0.topCandidates(1).first?.string }.filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }
                requestSummary = OCRSupport.parse(outputLines, fallbackCurrency: fallbackCurrency)
                semaphore.signal()
            }
            request.recognitionLevel = .accurate; request.recognitionLanguages = selectedLanguages
            do { try VNImageRequestHandler(cgImage: cgImage).perform([request]); semaphore.wait() } catch { outputLines = ["L’analyse a échoué. Vérifiez la lumière et réessayez."] }
            return (outputLines, requestSummary)
        }.value
        recognizedLines = result.lines.isEmpty ? ["Aucun texte lisible détecté. Rapprochez le document et améliorez la lumière."] : result.lines
        summary = result.summary
        suspectLines = Set(result.lines.filter { line in
            let lower = line.lowercased()
            let hasSensitiveLabel = lower.range(of: #"\\b(commission|surcharge|supplement)\\b"#, options: .regularExpression) != nil
            let hasExtremeAmount = result.summary.amounts.contains { $0 > 1000 }
            return hasSensitiveLabel && hasExtremeAmount
        })
        isAnalyzing = false
    }
}

extension OCRSupport {
    static func prepareImage(_ image: UIImage) -> UIImage? {
        let maxWidth: CGFloat = 2200; let scale = min(1, maxWidth / max(image.size.width, 1)); let size = CGSize(width: image.size.width * scale, height: image.size.height * scale)
        let renderer = UIGraphicsImageRenderer(size: size); let normalized = renderer.image { _ in image.draw(in: CGRect(origin: .zero, size: size)) }
        guard let input = CIImage(image: normalized), let filter = CIFilter(name: "CIColorControls") else { return normalized }
        filter.setValue(input, forKey: kCIInputImageKey); filter.setValue(1.15, forKey: kCIInputContrastKey); filter.setValue(0.05, forKey: kCIInputBrightnessKey)
        guard let output = filter.outputImage, let cg = CIContext().createCGImage(output, from: output.extent) else { return normalized }
        return UIImage(cgImage: cg, scale: normalized.scale, orientation: .up)
    }
}

struct CameraPicker: UIViewControllerRepresentable { let onImage: (UIImage) -> Void; func makeCoordinator() -> Coordinator { Coordinator(onImage: onImage) }; func makeUIViewController(context: Context) -> UIViewController { guard UIImagePickerController.isSourceTypeAvailable(.camera) else { let alert = UIAlertController(title: "Caméra indisponible", message: "Choisissez une photo depuis votre bibliothèque.", preferredStyle: .alert); alert.addAction(UIAlertAction(title: "OK", style: .default)); return alert }; let picker = UIImagePickerController(); picker.sourceType = .camera; picker.delegate = context.coordinator; return picker }; func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}; final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate { let onImage: (UIImage) -> Void; init(onImage: @escaping (UIImage) -> Void) { self.onImage = onImage }; func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) { if let image = info[.originalImage] as? UIImage { onImage(image) }; picker.dismiss(animated: true) }; func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { picker.dismiss(animated: true) } } }