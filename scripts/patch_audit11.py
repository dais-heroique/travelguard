from pathlib import Path

path = Path('/home/ubuntu/travelguard/scripts/generate_native_ios.py')
text = path.read_text()

text = text.replace('    @Published private(set) var country = ""\n', '    @Published private(set) var country = ""\n    @Published private(set) var countryCode = ""\n    @Published private(set) var proximityAlertsEnabled = false\n')
text = text.replace('        if UserDefaults.standard.bool(forKey: "alertsEnabled") { restoreProximityAlertsIfAuthorized() }\n', '        proximityAlertsEnabled = UserDefaults.standard.bool(forKey: "alertsEnabled") && !trustedRisks.isEmpty\n        if proximityAlertsEnabled { restoreProximityAlertsIfAuthorized() }\n')
text = text.replace('''        if hasPermission { manager.startUpdatingLocation() } else if permissionDenied { errorMessage = "Autorisation refusée. Vous pouvez l’activer dans Réglages." }\n''', '''        if hasPermission {\n            manager.startUpdatingLocation()\n            if authorization == .authorizedAlways && proximityAlertsEnabled { monitorRiskRegions() }\n        } else if permissionDenied { errorMessage = "Autorisation refusée. Vous pouvez l’activer dans Réglages." }\n''')
text = text.replace('''    func setProximityAlerts(_ enabled: Bool) {\n        UserDefaults.standard.set(enabled, forKey: "alertsEnabled")\n        if !enabled {\n            trustedRisks.forEach { manager.stopMonitoring(for: CLCircularRegion(center: CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude), radius: 250, identifier: $0.id)) }\n            return\n        }\n        if authorization == .authorizedWhenInUse { manager.requestAlwaysAuthorization() }\n        Task {\n            let granted = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])\n            guard granted == true else { return }\n            await MainActor.run {\n                guard self.authorization == .authorizedAlways else {\n                    self.errorMessage = "Les alertes en arrière-plan nécessitent l’autorisation Toujours."\n                    return\n                }\n                self.monitorRiskRegions()\n            }\n        }\n    }\n''', '''    func setProximityAlerts(_ enabled: Bool) {\n        guard enabled, !trustedRisks.isEmpty else {\n            proximityAlertsEnabled = false\n            UserDefaults.standard.set(false, forKey: "alertsEnabled")\n            manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }\n            return\n        }\n        proximityAlertsEnabled = true\n        UserDefaults.standard.set(true, forKey: "alertsEnabled")\n        if authorization == .authorizedWhenInUse { manager.requestAlwaysAuthorization() }\n        Task {\n            let granted = (try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])) == true\n            let settings = await UNUserNotificationCenter.current().notificationSettings()\n            await MainActor.run {\n                self.notificationPermission = settings.authorizationStatus\n                guard granted, settings.authorizationStatus == .authorized, self.authorization == .authorizedAlways else {\n                    self.proximityAlertsEnabled = false\n                    UserDefaults.standard.set(false, forKey: "alertsEnabled")\n                    self.errorMessage = self.authorization == .authorizedAlways ? "Les notifications sont nécessaires pour les alertes de proximité." : "Les alertes en arrière-plan nécessitent l’autorisation Toujours."\n                    return\n                }\n                self.monitorRiskRegions()\n            }\n        }\n    }\n''')
text = text.replace('''    private func monitorRiskRegions() {\n        for risk in trustedRisks {\n            let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: 250, identifier: risk.id)\n            region.notifyOnEntry = true\n            manager.startMonitoring(for: region)\n        }\n    }\n''', '''    private func monitorRiskRegions() {\n        guard authorization == .authorizedAlways, proximityAlertsEnabled else { return }\n        let current = coordinate\n        let nearby = trustedRisks\n            .filter { risk in (risk.distance(from: current) ?? .greatestFiniteMagnitude) <= 10000 }\n            .sorted { ($0.distance(from: current) ?? .greatestFiniteMagnitude) < ($1.distance(from: current) ?? .greatestFiniteMagnitude) }\n            .prefix(20)\n        let desiredIDs = Set(nearby.map(\\.id))\n        manager.monitoredRegions.filter { !desiredIDs.contains($0.identifier) }.forEach { manager.stopMonitoring(for: $0) }\n        for risk in nearby where !manager.monitoredRegions.contains(where: { $0.identifier == risk.id }) {\n            let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: 250, identifier: risk.id)\n            region.notifyOnEntry = true\n            manager.startMonitoring(for: region)\n        }\n    }\n''')
text = text.replace('''        country = UserDefaults.standard.string(forKey: "lastCountry") ?? ""\n        lastUpdated = timestamp\n''', '''        country = UserDefaults.standard.string(forKey: "lastCountry") ?? ""\n        countryCode = UserDefaults.standard.string(forKey: "lastCountryCode") ?? ""\n        lastUpdated = timestamp\n''')
text = text.replace('''                self.city = place.locality ?? place.subAdministrativeArea ?? place.administrativeArea ?? "Position détectée"\n                self.country = place.country ?? ""\n                UserDefaults.standard.set(self.city, forKey: "lastCity")\n                UserDefaults.standard.set(self.country, forKey: "lastCountry")\n''', '''                self.city = place.locality ?? place.subAdministrativeArea ?? place.administrativeArea ?? "Position détectée"\n                self.country = place.country ?? ""\n                self.countryCode = place.isoCountryCode ?? ""\n                UserDefaults.standard.set(self.city, forKey: "lastCity")\n                UserDefaults.standard.set(self.country, forKey: "lastCountry")\n                UserDefaults.standard.set(self.countryCode, forKey: "lastCountryCode")\n                if self.proximityAlertsEnabled { self.monitorRiskRegions() }\n''')

start = text.index("'ScannerView.swift': r'''" )
end = text.index("''',\n'SafetyView.swift':", start)
scanner = r'''\'ScannerView.swift\': r\'\'\'import CoreImage
import Foundation
import PhotosUI
import SwiftUI
import UIKit
import Vision

enum OCRSupport {
    static let amountPattern = #"(?<![0-9])([0-9]{1,3}(?:[ .\\u{00A0}][0-9]{3})*(?:[.,][0-9]{1,2})?|[0-9]+(?:[.,][0-9]{1,2})?)\\s*(€|EUR|USD|\\$|£|GBP|CHF)?"#
    static let labelPattern = #"\\b(total|subtotal|sous[- ]?total|amount due|à payer|a payer|taxe?|tva|vat|service|tip|service charge|frais|commission|surcharge|supplement)\\b"#

    static func normalizeNumber(_ raw: String) -> Double? {
        var value = raw.replacingOccurrences(of: " ", with: "").replacingOccurrences(of: "\\u{00A0}", with: "")
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
        switch countryCode.uppercased() { case "US", "CA": return "USD"; case "GB": return "GBP"; case "CH": return "CHF"; case "JP": return "JPY"; default: return "EUR" }
    }

    static func parse(_ lines: [String], fallbackCurrency: String) -> OCRSummary {
        var result = OCRSummary(); result.currency = fallbackCurrency
        let regex = try? NSRegularExpression(pattern: amountPattern, options: .caseInsensitive)
        for line in lines {
            let lower = line.lowercased()
            if lower.range(of: #"\\b[0-9]{1,2}[./-][0-9]{1,2}[./-][0-9]{2,4}\\b"#, options: .regularExpression) != nil { continue }
            let matches = regex?.matches(in: line, range: NSRange(line.startIndex..., in: line)) ?? []
            guard let match = matches.last, let numberRange = Range(match.range(at: 1), in: line), let value = normalizeNumber(String(line[numberRange])) else { continue }
            if let symbolRange = Range(match.range(at: 2), in: line), !String(line[symbolRange]).isEmpty { result.currency = String(line[symbolRange]) }
            result.amounts.append(value)
            let isTotal = lower.range(of: #"\\b(total|amount due|à payer|a payer)\\b"#, options: .regularExpression) != nil
            let isSubtotal = lower.range(of: #"\\b(subtotal|sous[- ]?total)\\b"#, options: .regularExpression) != nil
            let isTax = lower.range(of: #"\\b(taxe?|tva|vat)\\b"#, options: .regularExpression) != nil
            let isService = lower.range(of: #"\\b(service|tip|service charge|frais|commission|surcharge|supplement)\\b"#, options: .regularExpression) != nil
            if isTotal { result.total = value } else if isSubtotal { result.subtotal = value } else if isTax { result.tax = value } else if isService { result.service = value } else if !isTotal && !isTax && !isService { result.itemAmounts.append(value) }
        }
        return result
    }
}

struct OCRSummary {
    var currency = ""
    var subtotal: Double?
    var tax: Double?
    var service: Double?
    var total: Double?
    var amounts: [Double] = []
    var itemAmounts: [Double] = []
    var calculatedTotal: Double? {
        let base = itemAmounts.isEmpty ? subtotal : itemAmounts.reduce(0, +)
        guard let base else { return nil }
        return base + (tax ?? 0) + (service ?? 0)
    }
    var difference: Double? { guard let total, let calculatedTotal else { return nil }; return total - calculatedTotal }
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
            Text("Cadrez un menu, une addition ou un billet. L’analyse est locale et indicative : aucune conclusion officielle n’est inventée.").foregroundStyle(TGColor.muted)
            Button { showingCamera = true } label: { Label("Prendre une photo", systemImage: "camera.fill").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)) }
            PhotosPicker(selection: $selectedItem, matching: .images) { Label("Choisir une photo", systemImage: "photo").font(.headline).foregroundStyle(TGColor.ink).frame(maxWidth: .infinity).padding().background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) }.onChange(of: selectedItem) { _, item in Task { await analyze(item) } }
            if isAnalyzing { ProgressView("Analyse locale du document…").padding(.vertical) }
            if !recognizedLines.isEmpty { VStack(alignment: .leading, spacing: 10) {
                Label("Résultat du contrôle", systemImage: suspectLines.isEmpty ? "checkmark.circle.fill" : "exclamationmark.triangle.fill").font(.headline).foregroundStyle(suspectLines.isEmpty ? .green : TGColor.coral)
                ForEach(recognizedLines, id: \\.self) { line in Text(line).font(.body.weight(suspectLines.contains(line) ? .semibold : .regular)).foregroundStyle(suspectLines.contains(line) ? .red : TGColor.ink).padding(.vertical, 3) }
                if !suspectLines.isEmpty { Text("Vérifiez les frais, taxes, commissions et suppléments avant de payer.").font(.footnote).foregroundStyle(.red) }
                if summary.hasData { VStack(alignment: .leading, spacing: 6) { Text("Lecture structurée").font(.subheadline.bold()); if !summary.itemAmounts.isEmpty { Text("Articles détectés : \(summary.itemAmounts.reduce(0, +), specifier: \"%.2f\") \(summary.currency)") }; if let subtotal = summary.subtotal { Text("Sous-total indiqué : \(subtotal, specifier: \"%.2f\") \(summary.currency)") }; if let tax = summary.tax { Text("Taxes : \(tax, specifier: \"%.2f\") \(summary.currency)") }; if let service = summary.service { Text("Service : \(service, specifier: \"%.2f\") \(summary.currency)") }; if let total = summary.total { Text("Total détecté : \(total, specifier: \"%.2f\") \(summary.currency)").fontWeight(.bold) }; if let calculated = summary.calculatedTotal, let difference = summary.difference { Text(abs(difference) <= 0.05 ? "Total cohérent avec les lignes détectées : \(calculated, specifier: \"%.2f\") \(summary.currency)" : "Écart arithmétique à vérifier : \(difference, specifier: \"%.2f\") \(summary.currency)").foregroundStyle(abs(difference) <= 0.05 ? .green : .red).font(.footnote.bold()) }; Text("La comparaison à un tarif officiel n’est pas disponible sans source locale autorisée.").font(.caption).foregroundStyle(TGColor.muted) }.padding(.top, 8) }
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
        suspectLines = Set(result.lines.filter { line in line.range(of: OCRSupport.labelPattern, options: .regularExpression) != nil && line.range(of: OCRSupport.amountPattern, options: .regularExpression) != nil })
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
'''
text = text[:start] + scanner + text[end:]

text = text.replace('    private let cacheLifetime: TimeInterval = 24 * 60 * 60\n', '')
text = text.replace('    private let geocoder = CLGeocoder()\n', '    private let geocoder = CLGeocoder()\n    private let cacheLifetime: TimeInterval = 24 * 60 * 60\n')
text = text.replace('let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude), radius: 250, identifier: $0.id)', 'let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude), radius: 250, identifier: $0.id)')
path.write_text(text)
print('patched audit 11')
