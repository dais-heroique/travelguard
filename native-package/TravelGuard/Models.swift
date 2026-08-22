import CoreLocation
import Foundation
import MapKit

enum SourceTrust: String, Codable, Hashable { case government, officialPartner, verifiedCommunity, unknown }
enum EvidenceType: String, Codable, Hashable { case officialNotice, partnerReport, communityReport, observation, unknown }
enum LocationPrecision: String, Codable, Hashable { case point, neighborhood, city, country }

struct VerifiedSource: Codable, Hashable { let id: String; let name: String; let type: SourceTrust; let url: String }

struct RiskEvidence: Codable, Hashable {
    let id: String
    let sourceId: String
    let type: EvidenceType
    let observedAt: Date
    let verified: Bool
    enum CodingKeys: String, CodingKey { case id, sourceId, source, type, observedAt, verified }
    init(id: String, sourceId: String, type: EvidenceType, observedAt: Date, verified: Bool) { self.id = id; self.sourceId = sourceId; self.type = type; self.observedAt = observedAt; self.verified = verified }
    init(from decoder: Decoder) throws { let c = try decoder.container(keyedBy: CodingKeys.self); id = try c.decode(String.self, forKey: .id); sourceId = try c.decodeIfPresent(String.self, forKey: .sourceId) ?? (try c.decodeIfPresent(String.self, forKey: .source) ?? ""); type = try c.decodeIfPresent(EvidenceType.self, forKey: .type) ?? .unknown; observedAt = try c.decode(Date.self, forKey: .observedAt); verified = try c.decodeIfPresent(Bool.self, forKey: .verified) ?? false }
    func encode(to encoder: Encoder) throws { var c = encoder.container(keyedBy: CodingKeys.self); try c.encode(id, forKey: .id); try c.encode(sourceId, forKey: .sourceId); try c.encode(type, forKey: .type); try c.encode(observedAt, forKey: .observedAt); try c.encode(verified, forKey: .verified) }
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
        var bestByCell: [String: RiskPlace] = [:]
        let zoomBucket = latDelta > 60 || lonDelta > 60 ? 0 : latDelta > 20 || lonDelta > 20 ? 1 : 2
        let cellDivisor = [16.0, 24.0, 32.0][zoomBucket]
        for risk in ranked {
            let mapPoint = MKMapPoint(CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude))
            let pointCellWidth = max(256.0, min(8192.0, rect?.width ?? 1024.0) / cellDivisor)
            let pointCellHeight = max(256.0, min(8192.0, rect?.height ?? 1024.0) / cellDivisor)
            let wrappedX = mapPoint.x.truncatingRemainder(dividingBy: MKMapRect.world.width)
            let cell = "\(Int(wrappedX / pointCellWidth)):\(Int(mapPoint.y / pointCellHeight))"
            if let existing = bestByCell[cell] {
                let existingRelevance = Double(existing.score) * 0.7 + Double(existing.reliabilityIndex) * 0.3
                let candidateRelevance = Double(risk.score) * 0.7 + Double(risk.reliabilityIndex) * 0.3
                if candidateRelevance > existingRelevance { bestByCell[cell] = risk }
            } else { bestByCell[cell] = risk }
        }
        return bestByCell.values.sorted { left, right in
            let leftValue = Double(left.score) * 0.7 + Double(left.reliabilityIndex) * 0.3
            let rightValue = Double(right.score) * 0.7 + Double(right.reliabilityIndex) * 0.3
            return leftValue > rightValue
        }.prefix(limit).map { $0 }
    }

    static func validated(_ risks: [RiskPlace]) -> [RiskPlace] {
        var ids = Set<String>(); var result: [RiskPlace] = []
        for risk in risks {
            let sourceURLIsValid: Bool = { guard let record = risk.sourceRecord, let url = URL(string: record.url), url.scheme?.lowercased() == "https", let host = url.host, !host.isEmpty, !host.hasPrefix("localhost"), !host.hasPrefix("127."), !host.hasPrefix("10."), !host.hasPrefix("192.168."), !host.hasPrefix("169.254."), host != "::1", !host.hasPrefix("fc"), !host.hasPrefix("fd") else { return risk.sourceRecord == nil }; return true }()
            let evidenceIsRelated = risk.evidence.allSatisfy { evidence in risk.sourceRecord?.id == evidence.sourceId }
            let valid = !risk.id.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && ids.insert(risk.id).inserted && !risk.name.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !risk.category.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !risk.summary.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !risk.source.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && risk.latitude.isFinite && risk.longitude.isFinite && (-90...90).contains(risk.latitude) && (-180...180).contains(risk.longitude) && (0...100).contains(risk.score) && risk.reportCount >= 0 && risk.updatedAt <= Date().addingTimeInterval(300) && risk.updatedAt >= Date().addingTimeInterval(-365 * 24 * 60 * 60) && risk.revokedAt == nil && risk.alertRadius.isFinite && (1...5000).contains(risk.alertRadius) && Set(risk.evidence.map(\.id)).count == risk.evidence.count && Set(risk.evidence.map(\.sourceId)).count == risk.evidence.count && (risk.locationPrecision == .point || risk.sourceRecord != nil) && (risk.sourceRecord == nil || (risk.sourceRecord?.type == risk.sourceType && risk.sourceRecord?.name == risk.source && evidenceIsRelated)) && sourceURLIsValid
            if valid { result.append(risk) }
        }
        return result
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
    let sourceRecord: VerifiedSource?
    let locationPrecision: LocationPrecision
    let serverReliabilityIndex: Int?

    init(id: String, name: String, category: String, score: Int, summary: String, latitude: Double, longitude: Double, signals: [String] = [], source: String, updatedAt: Date, reportCount: Int = 0, sourceType: SourceTrust = .unknown, evidence: [RiskEvidence] = [], alertRadius: CLLocationDistance = 250, revokedAt: Date? = nil, sourceRecord: VerifiedSource? = nil, locationPrecision: LocationPrecision = .point, serverReliabilityIndex: Int? = nil) {
        let normalizedReliability = serverReliabilityIndex.map { min(100, max(0, $0)) }
        self.id = id
        self.name = name
        self.category = category
        self.score = score
        self.summary = summary
        self.latitude = latitude
        self.longitude = longitude
        self.signals = signals
        self.source = source
        self.updatedAt = updatedAt
        self.reportCount = reportCount
        self.sourceType = sourceType
        self.evidence = evidence
        self.alertRadius = alertRadius
        self.revokedAt = revokedAt
        self.sourceRecord = sourceRecord
        self.locationPrecision = locationPrecision
        self.serverReliabilityIndex = normalizedReliability
    }

    enum CodingKeys: String, CodingKey { case id, name, category, score, summary, latitude, longitude, signals, source, updatedAt, reportCount, sourceType, evidence, alertRadius, revokedAt, sourceRecord, locationPrecision, reliabilityIndex, confidenceScore }
    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try c.decode(String.self, forKey: .id); name = try c.decode(String.self, forKey: .name); category = try c.decode(String.self, forKey: .category)
        score = try c.decode(Int.self, forKey: .score); summary = try c.decode(String.self, forKey: .summary); latitude = try c.decode(Double.self, forKey: .latitude); longitude = try c.decode(Double.self, forKey: .longitude)
        signals = try c.decodeIfPresent([String].self, forKey: .signals) ?? []; source = try c.decode(String.self, forKey: .source); updatedAt = try c.decode(Date.self, forKey: .updatedAt); reportCount = try c.decodeIfPresent(Int.self, forKey: .reportCount) ?? 0
        sourceType = try c.decodeIfPresent(SourceTrust.self, forKey: .sourceType) ?? .unknown; evidence = try c.decodeIfPresent([RiskEvidence].self, forKey: .evidence) ?? []; alertRadius = try c.decodeIfPresent(CLLocationDistance.self, forKey: .alertRadius) ?? 250; revokedAt = try c.decodeIfPresent(Date.self, forKey: .revokedAt); sourceRecord = try c.decodeIfPresent(VerifiedSource.self, forKey: .sourceRecord); locationPrecision = try c.decodeIfPresent(LocationPrecision.self, forKey: .locationPrecision) ?? .point; serverReliabilityIndex = try c.decodeIfPresent(Int.self, forKey: .reliabilityIndex) ?? c.decodeIfPresent(Int.self, forKey: .confidenceScore)
    }

    func encode(to encoder: Encoder) throws { var c = encoder.container(keyedBy: CodingKeys.self); try c.encode(id, forKey: .id); try c.encode(name, forKey: .name); try c.encode(category, forKey: .category); try c.encode(score, forKey: .score); try c.encode(summary, forKey: .summary); try c.encode(latitude, forKey: .latitude); try c.encode(longitude, forKey: .longitude); try c.encode(signals, forKey: .signals); try c.encode(source, forKey: .source); try c.encode(updatedAt, forKey: .updatedAt); try c.encode(reportCount, forKey: .reportCount); try c.encode(sourceType, forKey: .sourceType); try c.encode(evidence, forKey: .evidence); try c.encode(alertRadius, forKey: .alertRadius); try c.encodeIfPresent(revokedAt, forKey: .revokedAt); try c.encodeIfPresent(sourceRecord, forKey: .sourceRecord); try c.encode(locationPrecision, forKey: .locationPrecision); try c.encodeIfPresent(serverReliabilityIndex, forKey: .reliabilityIndex) }

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
        let deduplicatedReports = min(8, max(0, Set(evidence.map(\.sourceId)).count))
        let reportSignal = min(10, deduplicatedReports)
        let localScore = min(100, max(0, freshness + sourceSignal + evidenceSignal + reportSignal))
        return serverReliabilityIndex.map { min(100, max(0, $0)) } ?? localScore
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
    let bbox: RiskBoundingBox?
    let etag: String?
    let expiresAt: Date?
}

struct RiskFeedEnvelope: Codable { let schemaVersion: Int; let fetchedAt: Date; let updatedAt: Date?; let page: Int?; let pageSize: Int?; let hasMore: Bool?; let risks: [RiskPlace] }

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

struct RiskBoundingBox: Codable, Hashable { let west: Double; let south: Double; let east: Double; let north: Double; let page: Int; let pageSize: Int = 100
    var isValid: Bool { west.isFinite && east.isFinite && south.isFinite && north.isFinite && (-180...180).contains(west) && (-180...180).contains(east) && (-90...90).contains(south) && (-90...90).contains(north) && page >= 1 && (1...500).contains(pageSize) }
    var longitudeSpan: Double { west <= east ? east - west : (180 - west) + (east + 180) }
}

protocol RiskRepository {
    func fetchRisks() async throws -> [RiskPlace]
    func fetchRisks(in bbox: RiskBoundingBox) async throws -> [RiskPlace]
}

enum RiskRepositoryError: Error { case unavailable, notModified, invalidResponse }
struct RiskRepositoryUnavailable: Error {}

/// No worldwide public risk feed is assumed. The production app stays empty rather than inventing risk data.
struct UnavailableRiskRepository: RiskRepository {
    func fetchRisks() async throws -> [RiskPlace] { throw RiskRepositoryUnavailable() }
    func fetchRisks(in bbox: RiskBoundingBox) async throws -> [RiskPlace] { throw RiskRepositoryUnavailable() }
}

struct RemoteRiskRepository: RiskRepository {
    let endpoint: URL?
    let allowedHost: String?
    private let maxResponseBytes = 8 * 1024 * 1024
    private let maxRisks = 5000
    func fetchRisks() async throws -> [RiskPlace] { throw RiskRepositoryError.unavailable }
    func fetchRisks(in bbox: RiskBoundingBox) async throws -> [RiskPlace] {
        guard bbox.isValid, bbox.longitudeSpan <= 180, let endpoint, endpoint.scheme?.lowercased() == "https", let host = endpoint.host, let allowedHost, !allowedHost.isEmpty, host == allowedHost, !host.hasPrefix("localhost"), !host.hasPrefix("127."), !host.hasPrefix("10."), !host.hasPrefix("192.168."), !host.hasPrefix("169.254."), host != "::1", !host.hasPrefix("fc"), !host.hasPrefix("fd") else { throw RiskRepositoryError.unavailable }
        var components = URLComponents(url: endpoint, resolvingAgainstBaseURL: false)!; components.queryItems = [URLQueryItem(name: "west", value: String(bbox.west)), URLQueryItem(name: "south", value: String(bbox.south)), URLQueryItem(name: "east", value: String(bbox.east)), URLQueryItem(name: "north", value: String(bbox.north)), URLQueryItem(name: "page", value: String(bbox.page)), URLQueryItem(name: "pageSize", value: String(bbox.pageSize))]
        guard let regionalEndpoint = components.url else { throw RiskRepositoryError.unavailable }
        var lastError: Error?
        for delay in [0.0, 1.0, 3.0, 10.0] {
            if delay > 0 { try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000)) }
            do {
                var request = URLRequest(url: regionalEndpoint); request.timeoutInterval = 8; request.cachePolicy = .reloadIgnoringLocalCacheData; request.setValue("application/json", forHTTPHeaderField: "Accept")
                if let etag = UserDefaults.standard.string(forKey: "travelguard.feed.etag") { request.setValue(etag, forHTTPHeaderField: "If-None-Match") }
                let (data, response) = try await URLSession.shared.data(for: request)
                guard let http = response as? HTTPURLResponse else { throw RiskRepositoryError.invalidResponse }
                if http.statusCode == 304 { throw RiskRepositoryError.notModified }
                guard (200..<300).contains(http.statusCode), data.count <= maxResponseBytes else {
                    if [401, 403, 404, 422].contains(http.statusCode) { throw RiskRepositoryError.invalidResponse }
                    throw RiskRepositoryError.unavailable
                }
                guard (http.value(forHTTPHeaderField: "Content-Type") ?? "").lowercased().contains("application/json") else { throw RiskRepositoryError.invalidResponse }
                if let etag = http.value(forHTTPHeaderField: "ETag") { UserDefaults.standard.set(etag, forKey: "travelguard.feed.etag") }
                let decoder = JSONDecoder(); decoder.dateDecodingStrategy = .iso8601
                let feed = try decoder.decode(RiskFeedEnvelope.self, from: data)
                guard feed.schemaVersion == 1, (feed.page ?? 1) >= 1, (feed.pageSize ?? feed.risks.count) <= maxRisks, feed.fetchedAt <= Date().addingTimeInterval(300), feed.risks.count <= maxRisks, feed.risks.allSatisfy({ risk in feed.updatedAt.map { risk.updatedAt >= $0.addingTimeInterval(-300) } ?? true }) else { throw RiskRepositoryError.invalidResponse }
                let validated = RiskPlace.validated(feed.risks)
                guard validated.count == feed.risks.count else { throw RiskRepositoryError.invalidResponse }
                return validated
            } catch { lastError = error; if case RiskRepositoryError.notModified = error { throw error }; if case RiskRepositoryError.invalidResponse = error { throw error } }
        }
        throw lastError ?? RiskRepositoryError.unavailable
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
