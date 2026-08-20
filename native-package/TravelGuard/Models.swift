import CoreLocation
import Foundation
import MapKit

enum SourceTrust: String, Codable, Hashable { case government, officialPartner, verifiedCommunity, unknown }

struct RiskEvidence: Codable, Hashable {
    let id: String
    let source: String
    let type: String
    let observedAt: Date
    let verified: Bool
}

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
        let limit = lonDelta > 60 || latDelta > 60 ? 80 : lonDelta > 20 || latDelta > 20 ? 180 : 300
        let center = CLLocation(latitude: region.center.latitude, longitude: region.center.longitude)
        let ranked = visible.sorted {
            let leftDistance = CLLocation(latitude: $0.latitude, longitude: $0.longitude).distance(from: center)
            let rightDistance = CLLocation(latitude: $1.latitude, longitude: $1.longitude).distance(from: center)
            let leftPriority = Double($0.score) * 0.55 + max(0, 1 - leftDistance / 100000) * 45
            let rightPriority = Double($1.score) * 0.55 + max(0, 1 - rightDistance / 100000) * 45
            return leftPriority > rightPriority
        }
        var occupiedCells = Set<String>()
        var selected: [RiskPlace] = []
        for risk in ranked {
            let mapPoint = MKMapPoint(CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude))
            let pointCellWidth = max(256.0, min(4096.0, rect?.width ?? 1024.0) / 24.0)
            let pointCellHeight = max(256.0, min(4096.0, rect?.height ?? 1024.0) / 24.0)
            let cell = "\(Int(mapPoint.x / pointCellWidth)):\(Int(mapPoint.y / pointCellHeight))"
            if occupiedCells.insert(cell).inserted { selected.append(risk) }
            if selected.count >= limit { break }
        }
        return selected
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
            risk.updatedAt <= Date().addingTimeInterval(300) && risk.updatedAt >= Date().addingTimeInterval(-365 * 24 * 60 * 60) &&
            risk.revokedAt == nil && !risk.evidence.contains(where: { !$0.observedAt.addingTimeInterval(365 * 24 * 60 * 60).isFuture }) &&
            (0...100).contains(risk.reliabilityIndex)
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
    let sourceType: SourceTrust
    let evidence: [RiskEvidence]
    let alertRadius: CLLocationDistance
    let revokedAt: Date?

    init(id: String, name: String, category: String, score: Int, summary: String, latitude: Double, longitude: Double, signals: [String] = [], source: String, updatedAt: Date, reportCount: Int = 0, sourceType: SourceTrust = .unknown, evidence: [RiskEvidence] = [], alertRadius: CLLocationDistance = 250, revokedAt: Date? = nil) { self.id = id; self.name = name; self.category = category; self.score = score; self.summary = summary; self.latitude = latitude; self.longitude = longitude; self.signals = signals; self.source = source; self.updatedAt = updatedAt; self.reportCount = reportCount; self.sourceType = sourceType; self.evidence = evidence; self.alertRadius = alertRadius; self.revokedAt = revokedAt }

    enum CodingKeys: String, CodingKey { case id, name, category, score, summary, latitude, longitude, signals, source, updatedAt, reportCount, sourceType, evidence, alertRadius, revokedAt }
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id); name = try c.decode(String.self, forKey: .name); category = try c.decode(String.self, forKey: .category)
        score = try c.decode(Int.self, forKey: .score); summary = try c.decode(String.self, forKey: .summary); latitude = try c.decode(Double.self, forKey: .latitude); longitude = try c.decode(Double.self, forKey: .longitude)
        signals = try c.decodeIfPresent([String].self, forKey: .signals) ?? []; source = try c.decode(String.self, forKey: .source); updatedAt = try c.decode(Date.self, forKey: .updatedAt); reportCount = try c.decodeIfPresent(Int.self, forKey: .reportCount) ?? 0
        sourceType = try c.decodeIfPresent(SourceTrust.self, forKey: .sourceType) ?? .unknown; evidence = try c.decodeIfPresent([RiskEvidence].self, forKey: .evidence) ?? []; alertRadius = try c.decodeIfPresent(CLLocationDistance.self, forKey: .alertRadius) ?? 250; revokedAt = try c.decodeIfPresent(Date.self, forKey: .revokedAt)
    }

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
    var reliabilityIndex: Int {
        let ageDays = max(0, Calendar.current.dateComponents([.day], from: updatedAt, to: Date()).day ?? 0)
        let freshness = max(0, 35 - min(ageDays, 35))
        let sourceSignal: Int = { switch sourceType { case .government: return 35; case .officialPartner: return 25; case .verifiedCommunity: return 12; case .unknown: return 0 } }()
        let uniqueEvidence = Set(evidence.map(\.id)).count
        let verifiedEvidence = evidence.filter(\.verified).count
        let evidenceSignal = min(20, uniqueEvidence * 3 + verifiedEvidence * 2)
        let deduplicatedReports = min(8, max(0, Set(evidence.map(\.source)).count))
        let reportSignal = min(10, deduplicatedReports)
        return min(100, max(0, freshness + sourceSignal + evidenceSignal + reportSignal))
    }
    var confidenceScore: Int { reliabilityIndex }
    var reliabilityLabel: String { "Indice de fiabilité : \(reliabilityIndex)/100" }

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

struct RiskFeedEnvelope: Codable { let schemaVersion: Int; let fetchedAt: Date; let risks: [RiskPlace] }

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

protocol RiskRepository {
    func fetchRisks() async throws -> [RiskPlace]
}

struct RiskRepositoryUnavailable: Error {}

/// No worldwide public risk feed is assumed. The production app stays empty rather than inventing risk data.
struct UnavailableRiskRepository: RiskRepository {
    func fetchRisks() async throws -> [RiskPlace] { throw RiskRepositoryUnavailable() }
}

struct RemoteRiskRepository: RiskRepository {
    let endpoint: URL?
    func fetchRisks() async throws -> [RiskPlace] {
        guard let endpoint else { throw RiskRepositoryUnavailable() }
        var request = URLRequest(url: endpoint); request.timeoutInterval = 15; request.cachePolicy = .reloadIgnoringLocalCacheData
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse, (200..<300).contains(http.statusCode) else { throw RiskRepositoryUnavailable() }
        let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
        let feed = try decoder.decode(RiskFeedEnvelope.self, from: data)
        guard feed.schemaVersion == 1, feed.fetchedAt <= Date().addingTimeInterval(300) else { throw RiskRepositoryUnavailable() }
        return RiskPlace.validated(feed.risks)
    }
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
