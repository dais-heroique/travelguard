import CoreLocation
import Foundation
import MapKit

struct RiskPlace: Identifiable, Hashable, Codable {
    static func inViewport(_ region: MKCoordinateRegion, risks: [RiskPlace]) -> [RiskPlace] {
        let latDelta = min(max(region.span.latitudeDelta, 0.0001), 180)
        let lonDelta = min(max(region.span.longitudeDelta, 0.0001), 360)
        let minLat = max(-90, region.center.latitude - latDelta / 2)
        let maxLat = min(90, region.center.latitude + latDelta / 2)
        let left = region.center.longitude - lonDelta / 2
        let right = region.center.longitude + lonDelta / 2
        let normalizedLeft = ((left + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
        let normalizedRight = ((right + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
        var rect: MKMapRect?
        if left >= -180 && right <= 180 {
            let a = MKMapPoint(CLLocationCoordinate2D(latitude: minLat, longitude: left))
            let b = MKMapPoint(CLLocationCoordinate2D(latitude: maxLat, longitude: right))
            rect = MKMapRect(x: min(a.x, b.x), y: min(a.y, b.y), width: abs(b.x - a.x), height: abs(b.y - a.y))
        }
        let visible = risks.filter { risk in
            guard risk.latitude >= minLat && risk.latitude <= maxLat else { return false }
            if let rect { return rect.contains(MKMapPoint(CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude))) }
            return risk.longitude >= normalizedLeft || risk.longitude <= normalizedRight
        }
        let limit = lonDelta > 60 || latDelta > 60 ? 120 : lonDelta > 20 || latDelta > 20 ? 300 : 1000
        return visible.sorted { $0.score > $1.score }.prefix(limit).map { $0 }
    }

    static func validated(_ risks: [RiskPlace]) -> [RiskPlace] {
        risks.filter { risk in
            !risk.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !risk.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !risk.category.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !risk.summary.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            !risk.source.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
            risk.latitude.isFinite && risk.longitude.isFinite &&
            (-90...90).contains(risk.latitude) && (-180...180).contains(risk.longitude) &&
            (0...100).contains(risk.score) && risk.reportCount >= 0 &&
            risk.updatedAt <= Date().addingTimeInterval(300) && risk.updatedAt >= Date().addingTimeInterval(-10 * 365 * 24 * 60 * 60) &&
            (0...100).contains(risk.confidenceScore)
        }
    }

    let id: String
    let name: String
    let category: String
    let score: Int
    let summary: String
    let latitude: Double
    let longitude: Double
    let signals: [String]
    let source: String
    let updatedAt: Date
    let reportCount: Int

    func distance(from coordinate: CLLocationCoordinate2D?) -> CLLocationDistance? {
        guard let coordinate else { return nil }
        return CLLocation(latitude: coordinate.latitude, longitude: coordinate.longitude).distance(from: CLLocation(latitude: latitude, longitude: longitude))
    }

    var freshnessLabel: String {
        let days = max(0, Calendar.current.dateComponents([.day], from: updatedAt, to: Date()).day ?? 0)
        return days == 0 ? "Mis à jour aujourd’hui" : "Mis à jour il y a \(days) j"
    }

    /// Product policy: 0–24 faible, 25–59 modéré, 60–79 élevé, 80–100 critique.
    var severityLabel: String {
        switch score { case 0..<25: return "faible"; case 25..<60: return "modéré"; case 60..<80: return "élevé"; default: return "critique" }
    }
    var confidenceScore: Int {
        let ageDays = max(0, Calendar.current.dateComponents([.day], from: updatedAt, to: Date()).day ?? 0)
        let freshness = max(0, 25 - min(ageDays, 25))
        let reportSignal = min(25, reportCount * 2)
        let sourceSignal = source.contains("démonstration") ? 0 : 25
        let completenessSignal = summary.isEmpty || signals.isEmpty ? 0 : 20
        return min(100, max(0, freshness + reportSignal + sourceSignal + completenessSignal))
    }

    func formattedDistance(from coordinate: CLLocationCoordinate2D?) -> String {
        guard let meters = distance(from: coordinate) else { return "Distance inconnue" }
        if meters < 1000 { return "\(Int(meters.rounded())) m" }
        return String(format: "%.1f km", meters / 1000).replacingOccurrences(of: ".0 km", with: " km")
    }
}

struct RiskCacheEnvelope: Codable {
    let schemaVersion: Int
    let savedAt: Date
    let risks: [RiskPlace]
}
struct FairPrice: Identifiable, Hashable {
    let id: String
    let label: String
    let value: String
    let reference: String
    let city: String
    let source: String
    let updatedAt: Date
}

struct SOSPhrase: Identifiable, Hashable {
    let id = UUID()
    let language: String
    let local: String
    let translation: String
}

private let localReferenceDate = Date(timeIntervalSince1970: 1754006400)

// Aucune donnée de risque ou de prix n’est embarquée sans source autorisée et traçable.
// Les intégrations locales doivent fournir coordonnées, date, source et score avant affichage.
let trustedRisks: [RiskPlace] = []

func prices(for city: String) -> [FairPrice] {
    []
}

struct OfficialSource: Identifiable, Hashable {
    let id: String
    let title: String
    let scope: String
    let url: String
}

let officialSources = [
    OfficialSource(id: "state-scams", title: "U.S. Department of State · Scams", scope: "Conseils officiels sur les arnaques de voyage", url: "https://travel.state.gov/en/international-travel/travel-advisories/scams.html"),
    OfficialSource(id: "state-advisories", title: "U.S. Department of State · Travel Advisories", scope: "Avertissements par pays", url: "https://travel.state.gov/en/international-travel/travel-advisories.html"),
    OfficialSource(id: "ftc-travel", title: "FTC · Avoid Scams When You Travel", scope: "Signaux d’arnaque et moyens de paiement", url: "https://consumer.ftc.gov/articles/avoid-scams-when-you-travel"),
    OfficialSource(id: "data-gov", title: "Data.gov · Travel Advisories", scope: "Catalogue de données publiques", url: "https://catalog.data.gov/dataset/travel-advisories")
]

let sampleSOS = [
    SOSPhrase(language: "Français", local: "Je veux le prix officiel, s’il vous plaît.", translation: "Phrase de contrôle du tarif"),
    SOSPhrase(language: "Anglais", local: "Please use the official meter.", translation: "Merci d’utiliser le compteur officiel."),
    SOSPhrase(language: "Espagnol", local: "Quiero el precio oficial, por favor.", translation: "Je veux le prix officiel, s’il vous plaît."),
    SOSPhrase(language: "Italien", local: "Vorrei il prezzo ufficiale, per favore.", translation: "Je voudrais le prix officiel, s’il vous plaît.")
]
