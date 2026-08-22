from pathlib import Path
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'native-package'
APP = ROOT / 'TravelGuard'
PROJ = ROOT / 'TravelGuard.xcodeproj'
APP.mkdir(parents=True, exist_ok=True)
(PROJ / 'project.xcworkspace').mkdir(parents=True, exist_ok=True)
(APP / 'Assets.xcassets' / 'AppIcon.appiconset').mkdir(parents=True, exist_ok=True)

files = {
'TravelGuardApp.swift': r'''import SwiftUI

@main
struct TravelGuardApp: App {
    @StateObject private var store = TravelGuardStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .preferredColorScheme(.light)
        }
    }
}
''',
'Models.swift': r'''import CoreLocation
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
''',
'Services.swift': r'''import Combine
import CoreLocation
import Foundation
import Network
import UserNotifications
import UIKit

@MainActor
final class LocationService: NSObject, ObservableObject, CLLocationManagerDelegate {
    @Published private(set) var authorization: CLAuthorizationStatus = .notDetermined
    @Published private(set) var servicesEnabled = true
    @Published private(set) var coordinate: CLLocationCoordinate2D?
    @Published private(set) var accuracy: CLLocationAccuracy?
    @Published private(set) var city = "Localisation requise"
    @Published private(set) var country = ""
    @Published private(set) var countryCode = ""
    @Published private(set) var proximityAlertsEnabled = false
    @Published private(set) var monitoringActive = false
    @Published private(set) var isUsingCachedLocation = false
    @Published private(set) var errorMessage: String?
    @Published private(set) var geocodingErrorMessage: String?
    @Published private(set) var lastUpdated: Date?
    @Published private(set) var requestCompletedAt: Date?
    @Published private(set) var notificationPermission: UNAuthorizationStatus = .notDetermined
    private let manager = CLLocationManager()
    private let geocoder = CLGeocoder()
    private let cacheLifetime: TimeInterval = 24 * 60 * 60

    private var lastGeocodeLocation: CLLocation?
    private var hasFreshLocationForAlerts = false
    private var monitoredRisks: [RiskPlace] = trustedRisks
    private var lastRegionRefreshLocation: CLLocation?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters
        manager.distanceFilter = 100
        manager.activityType = .otherNavigation
        manager.pausesLocationUpdatesAutomatically = true
        authorization = manager.authorizationStatus
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        restoreFreshCache()
        if hasPermission { manager.requestLocation() }
        proximityAlertsEnabled = UserDefaults.standard.bool(forKey: "alertsEnabled") && !monitoredRisks.isEmpty
        if proximityAlertsEnabled { restoreProximityAlertsIfAuthorized() }
    }

    var hasPermission: Bool { authorization == .authorizedWhenInUse || authorization == .authorizedAlways }
    var permissionDenied: Bool { authorization == .denied || authorization == .restricted }
    var cachedAgeLabel: String {
        guard let lastUpdated else { return "âge inconnu" }
        let seconds = max(0, Int(Date().timeIntervalSince(lastUpdated)))
        if seconds < 60 { return "à l’instant" }
        let minutes = seconds / 60
        if minutes < 60 { return "il y a \(minutes) min" }
        let hours = minutes / 60
        return "il y a \(hours) h"
    }
    var locationStatus: String {
        if !servicesEnabled { return "Services de localisation désactivés" }
        if permissionDenied { return "Autorisation de localisation refusée" }
        if coordinate == nil { return "Localisation en cours…" }
        if isUsingCachedLocation { return "Dernière position connue · \(cachedAgeLabel) · GPS en attente" }
        if let accuracy { return accuracy <= 50 ? "Position précise · ±\(Int(accuracy)) m" : accuracy <= 200 ? "Position approximative · ±\(Int(accuracy)) m" : "Position très imprécise · ±\(Int(accuracy)) m" }
        return "Position détectée"
    }

    func requestPermission() {
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        guard servicesEnabled else { errorMessage = "Activez la localisation dans Réglages pour utiliser les risques à proximité."; openSettings(); return }
                if hasPermission {
            manager.requestLocation()
        } else if permissionDenied { errorMessage = "Autorisation refusée. Ouvrez Réglages → TravelGuard → Localisation."; openSettings() } else { manager.requestWhenInUseAuthorization() }
    }

    private func openSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    func refresh() {
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        guard servicesEnabled, hasPermission else { return }
        manager.requestLocation()
    }

    func setProximityAlerts(_ enabled: Bool) {
        guard enabled, !monitoredRisks.isEmpty else {
            proximityAlertsEnabled = false
            UserDefaults.standard.set(false, forKey: "alertsEnabled")
            manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }
            manager.stopMonitoringSignificantLocationChanges()
            return
        }
        proximityAlertsEnabled = true
        monitoringActive = false
        UserDefaults.standard.set(true, forKey: "alertsEnabled")
        if authorization == .authorizedWhenInUse { manager.requestAlwaysAuthorization() }
        Task {
            let granted = (try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])) == true
            let settings = await UNUserNotificationCenter.current().notificationSettings()
            await MainActor.run {
                self.notificationPermission = settings.authorizationStatus
                guard granted, settings.authorizationStatus == .authorized else {
                    self.proximityAlertsEnabled = false
                    self.monitoringActive = false
                    UserDefaults.standard.set(false, forKey: "alertsEnabled")
                    self.errorMessage = "Les notifications sont nécessaires pour les alertes de proximité."
                    return
                }
                if self.authorization == .authorizedAlways { self.manager.startMonitoringSignificantLocationChanges(); self.manager.requestLocation() }
                else { self.errorMessage = "Autorisez la localisation Toujours pour installer les alertes autour de vous." }
            }
        }
    }

    func restoreProximityAlertsIfAuthorized() {
        UNUserNotificationCenter.current().getNotificationSettings { [weak self] settings in
            Task { @MainActor in
                guard let self else { return }
                self.notificationPermission = settings.authorizationStatus
                self.manager.monitoredRegions.forEach { self.manager.stopMonitoring(for: $0) }
                self.monitoringActive = false
                if settings.authorizationStatus == .authorized && self.authorization == .authorizedAlways { self.manager.startMonitoringSignificantLocationChanges(); self.manager.requestLocation() }
                else if settings.authorizationStatus != .authorized { self.proximityAlertsEnabled = false; self.monitoringActive = false; self.manager.stopMonitoringSignificantLocationChanges(); UserDefaults.standard.set(false, forKey: "alertsEnabled") }
            }
        }
    }

    func refreshMonitoredRegions() {
        guard hasFreshLocationForAlerts else { return }
        monitorRiskRegions()
    }

    /// Called by a future API/offline sync after replacing the authoritative risk set.
    func updateRisks(_ risks: [RiskPlace]) {
        monitoredRisks = RiskPlace.validated(risks)
        monitoringActive = false
        if monitoredRisks.isEmpty { proximityAlertsEnabled = false; UserDefaults.standard.set(false, forKey: "alertsEnabled"); manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }; manager.stopMonitoringSignificantLocationChanges(); return }
        if UserDefaults.standard.bool(forKey: "alertsEnabled") && authorization == .authorizedAlways {
            proximityAlertsEnabled = true
            manager.startMonitoringSignificantLocationChanges()
            manager.requestLocation()
        }
    }

    private func monitorRiskRegions() {
        guard authorization == .authorizedAlways, proximityAlertsEnabled, hasFreshLocationForAlerts, (accuracy ?? 999) <= 200, let current = coordinate else { monitoringActive = false; return }
        let validRisks = RiskPlace.validated(monitoredRisks)
        monitoredRisks = validRisks
        let nearby = validRisks
            .compactMap { risk -> (risk: RiskPlace, score: Double)? in
                guard risk.locationPrecision == .point, let distance = risk.distance(from: current), distance <= 10000 + risk.alertRadius else { return nil }
                let edgeDistanceScore = max(0, min(1, 1 - max(0, distance - risk.alertRadius) / 10000))
                let severityScore = min(1, max(0, Double(risk.score) / 100))
                let confidenceScore = min(1, max(0, Double(risk.confidenceScore) / 100))
                let monitoringScore = edgeDistanceScore * 0.5 + severityScore * 0.3 + confidenceScore * 0.2
                return (risk, monitoringScore)
            }
            .sorted { $0.score > $1.score }
            .prefix(20)
        let desiredIDs = Set(nearby.map { $0.risk.id })
        manager.monitoredRegions.filter { !desiredIDs.contains($0.identifier) }.forEach { manager.stopMonitoring(for: $0) }
        for entry in nearby {
            let risk = entry.risk
            guard !manager.monitoredRegions.contains(where: { $0.identifier == risk.id }) else { continue }
            let radius = min(max(risk.alertRadius, 100), 1000)
            let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: radius, identifier: risk.id)
            region.notifyOnEntry = true
            manager.startMonitoring(for: region)
        }
        lastRegionRefreshLocation = CLLocation(latitude: current.latitude, longitude: current.longitude)
        monitoringActive = !nearby.isEmpty
    }

    private func restoreFreshCache() {
        guard let latitude = UserDefaults.standard.object(forKey: "lastLatitude") as? Double,
              let longitude = UserDefaults.standard.object(forKey: "lastLongitude") as? Double,
              let timestamp = UserDefaults.standard.object(forKey: "lastLocationTimestamp") as? Date,
              Date().timeIntervalSince(timestamp) <= cacheLifetime else { return }
        coordinate = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        city = UserDefaults.standard.string(forKey: "lastCity") ?? "Dernière position connue"
        country = UserDefaults.standard.string(forKey: "lastCountry") ?? ""
        countryCode = UserDefaults.standard.string(forKey: "lastCountryCode") ?? ""
        lastUpdated = timestamp
        accuracy = UserDefaults.standard.object(forKey: "lastLocationAccuracy") as? Double
        isUsingCachedLocation = true
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorization = manager.authorizationStatus
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        if hasPermission {
            manager.requestLocation()
        } else if permissionDenied {
            if UserDefaults.standard.bool(forKey: "alertsEnabled") { proximityAlertsEnabled = false; monitoringActive = false; UserDefaults.standard.set(false, forKey: "alertsEnabled"); manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }; manager.stopMonitoringSignificantLocationChanges() }
            errorMessage = "Autorisation refusée. Vous pouvez l’activer dans Réglages."
        }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        requestCompletedAt = Date()
        guard let location = locations.last, location.horizontalAccuracy >= 0 else { return }
        coordinate = location.coordinate
        accuracy = location.horizontalAccuracy
        lastUpdated = Date()
        hasFreshLocationForAlerts = location.horizontalAccuracy <= 200
        isUsingCachedLocation = false
        if location.horizontalAccuracy > 200 { hasFreshLocationForAlerts = false; monitoringActive = false; return }
        errorMessage = location.horizontalAccuracy > 200 ? "Position très imprécise (±\(Int(location.horizontalAccuracy)) m) : distances et alertes désactivées." : location.horizontalAccuracy > 100 ? "Position GPS approximative (±\(Int(location.horizontalAccuracy)) m)." : nil
        UserDefaults.standard.set(location.coordinate.latitude, forKey: "lastLatitude")
        UserDefaults.standard.set(location.coordinate.longitude, forKey: "lastLongitude")
        UserDefaults.standard.set(location.horizontalAccuracy, forKey: "lastLocationAccuracy")
        UserDefaults.standard.set(Date(), forKey: "lastLocationTimestamp")
        if proximityAlertsEnabled, hasFreshLocationForAlerts, (lastRegionRefreshLocation == nil || lastRegionRefreshLocation?.distance(from: location) ?? .greatestFiniteMagnitude >= 500) { monitorRiskRegions() }
        let shouldGeocode = lastGeocodeLocation == nil || (lastGeocodeLocation?.distance(from: location) ?? .greatestFiniteMagnitude) > 2000
        guard shouldGeocode else { return }
        lastGeocodeLocation = location
        geocoder.cancelGeocode()
        geocoder.reverseGeocodeLocation(location) { [weak self] places, error in
            guard let self, error == nil, let place = places?.first else {
                Task { @MainActor in self?.geocodingErrorMessage = "Ville indisponible pour le moment ; la position GPS reste utilisable." }
                return
            }
            Task { @MainActor in
                self.geocodingErrorMessage = nil
                self.city = place.locality ?? place.subAdministrativeArea ?? place.administrativeArea ?? "Position détectée"
                self.country = place.country ?? ""
                self.countryCode = place.isoCountryCode ?? ""
                UserDefaults.standard.set(self.city, forKey: "lastCity")
                UserDefaults.standard.set(self.country, forKey: "lastCountry")
                UserDefaults.standard.set(self.countryCode, forKey: "lastCountryCode")
            }
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        requestCompletedAt = Date()
        let code = (error as? CLError)?.code
        print("[TravelGuard][Location] error=\(String(describing: code)) description=\(error.localizedDescription)")
        if code == .denied { errorMessage = "Autorisation de localisation refusée. Ouvrez Réglages." }
        else if code == .locationUnknown { errorMessage = "Position GPS temporairement indisponible. Réessayez dans quelques instants." }
        else { errorMessage = "Erreur GPS (\(code?.rawValue ?? -1)) : \(error.localizedDescription)" }
        if coordinate == nil { city = "Position indisponible" }
    }

    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        let cooldownKey = "travelguard.notificationCooldown.\(region.identifier)"
        let now = Date()
        if let previous = UserDefaults.standard.object(forKey: cooldownKey) as? Date, now.timeIntervalSince(previous) < 1800 { return }
        UserDefaults.standard.set(now, forKey: cooldownKey)
        guard let risk = monitoredRisks.first(where: { $0.id == region.identifier }), risk.revokedAt == nil else {
            manager.stopMonitoring(for: region)
            return
        }
        let content = UNMutableNotificationContent()
        content.title = "Risque \(risk.severityLabel) à proximité"
        let distance = risk.formattedDistance(from: coordinate)
        content.body = "\(risk.category) · \(distance) · \(risk.reliabilityLabel). Source : \(risk.source). \(risk.freshnessLabel). Vérifiez les prix avant de payer."
        content.sound = .default
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: "risk-\(region.identifier)", content: content, trigger: nil))
    }

}

@MainActor
final class NetworkMonitor: ObservableObject {
    @Published private(set) var isOnline = false
    @Published private(set) var isChecking = true
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "travelguard.network")

    init() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor in
                self?.isOnline = path.status == .satisfied
                self?.isChecking = false
            }
        }
        monitor.start(queue: queue)
    }

    deinit { monitor.cancel() }

}

@MainActor
final class TravelGuardStore: ObservableObject {
    @Published var onboardingComplete: Bool
    @Published var travelerProfile = UserDefaults.standard.string(forKey: "travelerProfile") ?? "Voyageur fréquent"
    @Published var priorities: Set<String> = Set(UserDefaults.standard.stringArray(forKey: "priorities") ?? [])
    @Published private(set) var risks: [RiskPlace]
    let location = LocationService()
    let network = NetworkMonitor()
    @Published var selectedTab = 0
    private let riskCacheURL: URL = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0].appendingPathComponent("travelguard-risks-v2.json")
    private let maxCachedRisks = 5000
    private let maxCacheBytes = 2 * 1024 * 1024
    private let cacheMaxAge: TimeInterval = 365 * 24 * 60 * 60
    @Published private(set) var lastRiskSyncAt: Date?
    private var latestRiskSyncGeneration = 0
    private let riskRepository: any RiskRepository
    @Published private(set) var riskSyncState = "Aucune source de risques configurée"
    var riskDataFreshnessLabel: String {
        guard let lastRiskSyncAt else { return "Données non synchronisées" }
        let minutes = max(0, Int(Date().timeIntervalSince(lastRiskSyncAt) / 60))
        if minutes < 60 { return "Données mises à jour il y a \(minutes) min" }
        return "Données mises à jour il y a \(minutes / 60) h"
    }
    var riskDataIsStale: Bool { guard let lastRiskSyncAt else { return true }; return Date().timeIntervalSince(lastRiskSyncAt) > 24 * 60 * 60 }
    var protectionStatusLabel: String {
        if !storeHasRisks { return "Alertes indisponibles" }
        if !location.hasPermission { return "Localisation nécessaire" }
        if location.accuracy ?? 999 > 200 { return "GPS imprécis" }
        if location.notificationPermission != .authorized || !location.monitoringActive { return riskDataIsStale ? "Données anciennes" : "Protection partielle" }
        if riskDataIsStale { return "Données anciennes" }
        return "Protection active"
    }
    var storeHasRisks: Bool { !risks.isEmpty }

    init(riskRepository: any RiskRepository = RemoteRiskRepository(endpoint: (Bundle.main.object(forInfoDictionaryKey: "RiskFeedURL") as? String).flatMap(URL.init(string:)), allowedHost: Bundle.main.object(forInfoDictionaryKey: "RiskFeedAllowedHost") as? String)) {
        self.riskRepository = riskRepository
        onboardingComplete = UserDefaults.standard.bool(forKey: "onboardingComplete")
        lastRiskSyncAt = nil
        try? FileManager.default.createDirectory(at: riskCacheURL.deletingLastPathComponent(), withIntermediateDirectories: true)
        if let data = try? Data(contentsOf: riskCacheURL), let envelope = try? JSONDecoder().decode(RiskCacheEnvelope.self, from: data), envelope.schemaVersion == 2, envelope.savedAt <= Date().addingTimeInterval(300), envelope.savedAt >= Date().addingTimeInterval(-cacheMaxAge) { risks = RiskPlace.validated(Array(envelope.risks.prefix(maxCachedRisks))); lastRiskSyncAt = envelope.savedAt } else { risks = trustedRisks }
        location.updateRisks(risks)
        location.restoreProximityAlertsIfAuthorized()
    }

    func beginRiskSync() -> Int { latestRiskSyncGeneration += 1; return latestRiskSyncGeneration }

    func synchronizeRisks() async {
        let generation = beginRiskSync()
        do {
            let incoming = try await riskRepository.fetchRisks()
            updateRisks(incoming, generation: generation)
            riskSyncState = incoming.isEmpty ? "Aucun risque validé reçu" : "Risques synchronisés"
        } catch {
            riskSyncState = "Source de risques indisponible"
        }
    }

    func synchronizeRisks(in bbox: RiskBoundingBox) async {
        let generation = beginRiskSync()
        do { let incoming = try await riskRepository.fetchRisks(in: bbox); updateRisks(incoming, generation: generation, merge: true, bbox: bbox); riskSyncState = incoming.isEmpty ? "Aucun risque validé reçu pour cette zone" : "Risques régionaux synchronisés" } catch { riskSyncState = "Source régionale indisponible" }
    }

    func updateRisks(_ incoming: [RiskPlace], generation: Int? = nil, merge: Bool = false, bbox: RiskBoundingBox? = nil) {
        if let generation, generation < latestRiskSyncGeneration { return }
        purgeNotificationCooldowns()
        if let generation { latestRiskSyncGeneration = generation }
        let validated = RiskPlace.validated(incoming)
        let combined: [RiskPlace] = merge ? Array(Dictionary(uniqueKeysWithValues: (risks + validated).map { ($0.id, $0) }).values) : validated
        risks = Array(combined.filter { Date().timeIntervalSince($0.updatedAt) <= cacheMaxAge }.prefix(maxCachedRisks))
        lastRiskSyncAt = Date()
        location.updateRisks(risks)
        let envelope = RiskCacheEnvelope(schemaVersion: 2, savedAt: lastRiskSyncAt ?? Date(), risks: risks, bbox: bbox, etag: UserDefaults.standard.string(forKey: "travelguard.feed.etag"), expiresAt: Date().addingTimeInterval(24 * 60 * 60))
        if let data = try? JSONEncoder().encode(envelope), data.count <= maxCacheBytes, risks.count <= maxCachedRisks { try? data.write(to: riskCacheURL, options: [.atomic]) }
    }

    private func purgeNotificationCooldowns() {
        let defaults = UserDefaults.standard
        defaults.dictionaryRepresentation().keys.filter { $0.hasPrefix("travelguard.notificationCooldown.") }.forEach { defaults.removeObject(forKey: $0) }
    }

    func completeOnboarding(profile: String, priorities: Set<String>) {
        travelerProfile = profile
        self.priorities = priorities
        UserDefaults.standard.set(profile, forKey: "travelerProfile")
        UserDefaults.standard.set(Array(priorities), forKey: "priorities")
        UserDefaults.standard.set(true, forKey: "onboardingComplete")
        onboardingComplete = true
    }
}
''',
'Theme.swift': r'''import SwiftUI

enum TGColor {
    static let ink = Color(red: 0.055, green: 0.12, blue: 0.18)
    static let teal = Color(red: 0.04, green: 0.52, blue: 0.55)
    static let mint = Color(red: 0.78, green: 0.95, blue: 0.91)
    static let ivory = Color(red: 0.98, green: 0.97, blue: 0.93)
    static let amber = Color(red: 0.95, green: 0.58, blue: 0.14)
    static let coral = Color(red: 0.86, green: 0.22, blue: 0.26)
    static let muted = Color(red: 0.38, green: 0.43, blue: 0.45)
}

extension View {
    func tgCard() -> some View {
        self.padding(16).background(.white).clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous)).overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(Color.black.opacity(0.07)))
    }
}
''',
'RootView.swift': r'''import SwiftUI

struct RootView: View {
    @EnvironmentObject private var store: TravelGuardStore

    var body: some View {
        Group {
            if store.onboardingComplete { MainTabView() } else { OnboardingView() }
        }
        .tint(TGColor.teal)
        .background(TGColor.ivory.ignoresSafeArea())
        .task { await store.synchronizeRisks() }
    }
}

struct MainTabView: View {
    @EnvironmentObject private var store: TravelGuardStore
    var body: some View {
        TabView(selection: $store.selectedTab) {
            HomeView().tabItem { Label("Accueil", systemImage: "house.fill") }.tag(0)
            RiskMapView().tabItem { Label("Carte", systemImage: "map.fill") }.tag(1)
            ScannerView().tabItem { Label("Scanner", systemImage: "viewfinder") }.tag(2)
            SafetyView().tabItem { Label("Sécurité", systemImage: "shield.fill") }.tag(3)
        }
    }
}
''',
'OnboardingView.swift': r'''import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var page = 0
    @State private var profile = "Voyageur fréquent"
    @State private var priorities: Set<String> = []
    private let pages = [
        ("BIENVENUE DANS TRAVELGUARD", "Votre bouclier avant de payer.", "Repérez les signaux faibles avant qu’ils ne coûtent cher.", "shield.fill"),
        ("PIÈGES À TOURISTES", "Voyez les risques autour de vous.", "Carte, scores de confiance et signaux locaux pour décider plus sereinement.", "map.fill"),
        ("SCANNER", "Contrôlez un menu ou un billet.", "Cadrez un document pour repérer les lignes inhabituelles et les prix à vérifier.", "viewfinder"),
        ("JUSTE PRIX", "Comparez avant de payer.", "Gardez des repères locaux pour les cafés, taxis et attractions.", "checkmark.seal.fill"),
        ("HORS LIGNE", "Vos réflexes restent disponibles.", "Les données enregistrées, les phrases SOS et les repères essentiels restent sur l’iPhone.", "wifi.slash"),
        ("VOTRE PROFIL", "Adaptons vos contrôles.", "Choisissez votre façon de voyager et les risques qui comptent le plus pour vous.", "person.crop.circle.fill"),
        ("ALERTES DE PROXIMITÉ", "Recevoir les bons signaux au bon moment.", "TravelGuard utilise votre position pendant l’utilisation pour afficher les risques autour de vous.", "location.fill")
    ]
    private let travelerOptions = ["Vacancier", "Backpacker", "Télétravailleur itinérant", "Voyageur fréquent"]
    private let priorityOptions = ["Menus gonflés", "Taxis abusifs", "Change douteux", "Billets non officiels"]

    var body: some View {
        VStack(spacing: 0) {
            HStack { Text("TG").font(.headline).foregroundStyle(.white).frame(width: 38, height: 38).background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 12)); Spacer(); Button("Passer") { finish() }.font(.subheadline.weight(.semibold)).foregroundStyle(TGColor.muted) }.padding(.horizontal, 20).padding(.top, 12)
            ProgressView(value: Double(page + 1), total: Double(pages.count)).tint(TGColor.teal).padding(.horizontal, 20).padding(.top, 14)
            TabView(selection: $page) {
                ForEach(Array(pages.enumerated()), id: \.offset) { index, item in
                    VStack(alignment: .leading, spacing: 18) {
                        Image(systemName: item.3).font(.system(size: 38, weight: .semibold)).foregroundStyle(TGColor.teal).frame(width: 82, height: 82).background(TGColor.mint).clipShape(RoundedRectangle(cornerRadius: 24))
                        Text(item.0).font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.teal)
                        Text(item.1).font(.system(size: 31, weight: .bold, design: .rounded)).foregroundStyle(TGColor.ink).fixedSize(horizontal: false, vertical: true)
                        Text(item.2).font(.body).foregroundStyle(TGColor.muted).lineSpacing(4)
                        if index == 5 { profilePicker }
                        Spacer()
                    }.padding(.horizontal, 24).padding(.top, 34).tag(index)
                }
            }.tabViewStyle(.page(indexDisplayMode: .never))
            VStack(spacing: 10) {
                if page == 5 { priorityPicker }
                Button(action: next) { Text(page == pages.count - 1 ? "Activer ma protection" : "Continuer").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding(.vertical, 16).contentShape(Rectangle()) }.buttonStyle(.plain).background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)).padding(.horizontal, 20).zIndex(2)
            }.padding(.bottom, 12)
        }.background(TGColor.ivory.ignoresSafeArea())
    }

    private var profilePicker: some View {
        VStack(alignment: .leading, spacing: 10) { Text("Votre profil").font(.headline).foregroundStyle(TGColor.ink); ForEach(travelerOptions, id: \.self) { option in Button { profile = option } label: { HStack { Text(option); Spacer(); Image(systemName: profile == option ? "checkmark.circle.fill" : "circle").foregroundStyle(profile == option ? TGColor.teal : TGColor.muted) } }.foregroundStyle(TGColor.ink).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 12)) } }
    }

    private var priorityPicker: some View {
        VStack(alignment: .leading, spacing: 8) { Text("Vos priorités").font(.headline).foregroundStyle(TGColor.ink); HStack { ForEach(priorityOptions, id: \.self) { option in Button { if priorities.contains(option) { priorities.remove(option) } else { priorities.insert(option) } } label: { Text(option).font(.caption.weight(.semibold)).padding(.horizontal, 10).padding(.vertical, 8).foregroundStyle(priorities.contains(option) ? .white : TGColor.ink).background(priorities.contains(option) ? TGColor.teal : .white).clipShape(Capsule()) } } } }
    }

    private func next() { if page < pages.count - 1 { withAnimation { page += 1 } } else { store.location.requestPermission(); finish() } }
    private func finish() { store.completeOnboarding(profile: profile, priorities: priorities) }
}
''',
'HomeView.swift': r'''import Foundation
import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var store: TravelGuardStore
    var place: String { store.location.country.isEmpty ? store.location.city : "\(store.location.city) · \(store.location.country)" }
    private var nearbyRisks: [RiskPlace] {
        guard let coordinate = store.location.coordinate else { return [] }
        return store.risks.filter { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) <= 10000 }.sorted { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) < ($1.distance(from: coordinate) ?? .greatestFiniteMagnitude) }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack { VStack(alignment: .leading, spacing: 4) { Text("TRAVELGUARD").font(.caption.weight(.heavy)).tracking(1.5).foregroundStyle(TGColor.muted); Text("Voyagez l’esprit léger.").font(.system(size: 29, weight: .bold, design: .rounded)).foregroundStyle(TGColor.ink) }; Spacer(); Text("TG").font(.headline).foregroundStyle(.white).frame(width: 42, height: 42).background(TGColor.teal).clipShape(Circle()) }
                    VStack(alignment: .leading, spacing: 12) {
                        Label(store.protectionStatusLabel.uppercased(), systemImage: store.protectionStatusLabel == "Protection active" ? "checkmark.shield.fill" : "exclamationmark.shield").font(.caption.weight(.heavy)).foregroundStyle(store.protectionStatusLabel == "Protection active" ? TGColor.mint : TGColor.amber)
                        Text(place).font(.title2.bold()).foregroundStyle(.white)
                        HStack(spacing: 14) { Label(store.location.locationStatus, systemImage: "location.fill"); Label(store.network.isOnline ? "En ligne" : "Hors ligne", systemImage: store.network.isOnline ? "wifi" : "wifi.slash") }.font(.caption.weight(.semibold)).foregroundStyle(.white.opacity(0.88))
                        Text(store.protectionStatusLabel == "Protection active" ? "Protection active · données surveillées" : store.protectionStatusLabel == "Données anciennes" ? "Protection partielle · données anciennes" : store.protectionStatusLabel == "GPS imprécis" ? "Protection partielle · GPS imprécis" : store.protectionStatusLabel).font(.subheadline).foregroundStyle(.white.opacity(0.86)); Text(store.riskDataFreshnessLabel).font(.caption).foregroundStyle(store.riskDataIsStale ? TGColor.amber : .white.opacity(0.72))
                        Divider().overlay(.white.opacity(0.25))
                        Text(store.location.coordinate == nil ? "Aucun risque local sans position fiable" : (store.location.accuracy ?? 999) > 200 ? "Position très imprécise : distances masquées" : (store.location.accuracy ?? 999) > 50 ? "Position approximative : distances indicatives" : nearbyRisks.isEmpty ? (store.riskDataIsStale ? "Aucun risque connu dans les données disponibles · données anciennes" : "Aucun risque connu à proximité") : "\(nearbyRisks.count) signaux géolocalisés sourcés dans un rayon de 10 km").font(.subheadline.bold()).foregroundStyle(.white).frame(maxWidth: .infinity, alignment: .leading)
                        ForEach(nearbyRisks.prefix(2)) { risk in HStack(spacing: 9) { Image(systemName: risk.category == "Taxi" ? "car.fill" : risk.category == "Change" ? "banknote.fill" : "fork.knife").font(.caption.bold()).foregroundStyle(.white).frame(width: 26, height: 26).background(TGColor.coral).clipShape(Circle()); VStack(alignment: .leading, spacing: 2) { Text(risk.category.uppercased()).font(.caption2.bold()).foregroundStyle(.white.opacity(0.72)); Text(risk.name).font(.caption.weight(.semibold)).foregroundStyle(.white) }; Spacer(); Text(((store.location.accuracy ?? 999) > 200 ? "Distance indisponible" : risk.formattedDistance(from: store.location.coordinate))).font(.caption.bold()).foregroundStyle(.white.opacity(0.9)) } }
                    }.padding(16).background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous)).overlay(RoundedRectangle(cornerRadius: 22, style: .continuous).stroke(TGColor.teal.opacity(0.35)))
                    Text("Besoin d’un contrôle rapide ?").font(.title3.bold()).foregroundStyle(TGColor.ink)
                    HStack(spacing: 10) { QuickLink(title: "Voir la carte", icon: "map.fill", tab: 1); QuickLink(title: "Scanner", icon: "viewfinder", tab: 2); QuickLink(title: "Juste prix", icon: "checkmark.seal.fill", tab: 3) }
                    Text("Références de prix · \(store.location.city)").font(.title3.bold()).foregroundStyle(TGColor.ink)
                    if prices(for: store.location.city).isEmpty { Text("Aucune référence officielle de prix n’est disponible hors ligne pour \(store.location.city). L’application ne fabrique pas de tarif.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() } else { ForEach(prices(for: store.location.city)) { price in HStack { Image(systemName: "checkmark.seal.fill").foregroundStyle(.green); VStack(alignment: .leading) { Text(price.label).font(.subheadline.bold()); Text(price.reference).font(.caption).foregroundStyle(TGColor.muted) }; Spacer(); Text(price.value).bold() }.tgCard() } }
                }.padding(.horizontal, 20).padding(.top, 10).padding(.bottom, 30)
            }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true)
        }
    }
}

struct QuickLink: View {
    @EnvironmentObject private var store: TravelGuardStore
    let title: String; let icon: String; let tab: Int
    var body: some View { Button { store.selectedTab = tab } label: { VStack(alignment: .leading, spacing: 10) { Image(systemName: icon).font(.title3).foregroundStyle(TGColor.teal); Text(title).font(.subheadline.weight(.bold)).foregroundStyle(TGColor.ink) }.frame(maxWidth: .infinity, minHeight: 82, alignment: .leading).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } }
}
''',
'RiskMapView.swift': r'''import Foundation
import MapKit
import SwiftUI
import UIKit

struct RiskMapLegend: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Label("Faible", systemImage: "circle.fill").foregroundStyle(.green)
            Label("Modéré", systemImage: "circle.fill").foregroundStyle(.orange)
            Label("Élevé", systemImage: "circle.fill").foregroundStyle(.red)
            Label("Zone", systemImage: "circle.dotted").foregroundStyle(.red)
        }
        .font(.caption2.bold())
        .padding(9)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

struct RiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 0, longitude: 0), span: MKCoordinateSpan(latitudeDelta: 45, longitudeDelta: 45))
    @State private var selected: RiskPlace?
    @State private var showFullScreen = false
    @State private var hasInitiallyCentered = false
    @State private var hasUserInteractedWithMap = false
    @State private var suppressNextCameraChange = false
    @State private var isRequestingPosition = false
    @State private var positionSearchTimedOut = false
    @State private var positionTask: Task<Void, Never>?
    @State private var viewportTask: Task<Void, Never>?

    private var displayedRisks: [RiskPlace] { RiskPlace.inViewport(region, risks: store.risks) }

    private func requestViewportRisks() {
        viewportTask?.cancel()
        let snapshot = region
        guard snapshot.span.latitudeDelta <= 90, snapshot.span.longitudeDelta <= 180 else { return }
        viewportTask = Task { @MainActor in
            try? await Task.sleep(nanoseconds: 400_000_000)
            guard !Task.isCancelled else { return }
            let lat = min(max(snapshot.span.latitudeDelta, 0.001), 90)
            let lon = min(max(snapshot.span.longitudeDelta, 0.001), 180)
            let west = ((snapshot.center.longitude - lon / 2 + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
            let east = ((snapshot.center.longitude + lon / 2 + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
            let south = max(-90, snapshot.center.latitude - lat / 2)
            let north = min(90, snapshot.center.latitude + lat / 2)
            await store.synchronizeRisks(in: RiskBoundingBox(west: west, south: south, east: east, north: north, page: 1))
        }
    }

    private func recenter() {
        positionTask?.cancel()
        positionTask = nil
        guard let coordinate = store.location.coordinate else {
            store.location.requestPermission()
            return
        }
        suppressNextCameraChange = true
        withAnimation {
            region = MKCoordinateRegion(center: coordinate, span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035))
        }
        hasInitiallyCentered = true
        isRequestingPosition = false
    }

    private func centerInitiallyIfNeeded() {
        guard !hasInitiallyCentered, !hasUserInteractedWithMap, store.location.coordinate != nil else { return }
        recenter()
    }

    private func zoom(by factor: Double) {
        suppressNextCameraChange = true
        hasUserInteractedWithMap = true
        let latitude = min(max(region.span.latitudeDelta * factor, 0.001), 180.0)
        let longitude = min(max(region.span.longitudeDelta * factor, 0.001), 360.0)
        withAnimation { region.span = MKCoordinateSpan(latitudeDelta: latitude, longitudeDelta: longitude) }
    }

    @ViewBuilder private func annotation(for risk: RiskPlace) -> some View {
        Button { selected = risk } label: {
            Image(systemName: risk.locationPrecision == .point ? "exclamationmark.triangle.fill" : "circle.dotted")
                .foregroundStyle(risk.score >= 60 ? .red : risk.score >= 30 ? .orange : .green)
                .padding(9)
                .background(.white)
                .clipShape(Circle())
                .shadow(radius: 3)
        }
        .accessibilityLabel("\(risk.name), risque \(risk.severityLabel), confiance \(risk.confidenceScore) pour cent")
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted)
                        Text("Carte des risques").font(.title.bold())
                    }
                    Spacer()
                    Text(store.location.city.isEmpty ? "Localisation…" : store.location.city)
                        .font(.caption.bold())
                        .padding(9)
                        .background(.white)
                        .clipShape(Capsule())
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                .padding(.bottom, 12)

                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in
                    MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) {
                        annotation(for: risk)
                    }
                }
                .onMapCameraChange(frequency: .onEnd) { _ in
                    if suppressNextCameraChange {
                        suppressNextCameraChange = false
                    } else {
                        hasUserInteractedWithMap = true
                        hasInitiallyCentered = true
                        requestViewportRisks()
                    }
                }
                .frame(height: min(max(UIScreen.main.bounds.height * 0.52, 420), 620))
                .overlay(alignment: .topLeading) { RiskMapLegend().padding(10) }
                .clipShape(RoundedRectangle(cornerRadius: 22))
                .padding(.horizontal, 20)

                if displayedRisks.isEmpty {
                    Text(store.risks.isEmpty ? "Aucun risque synchronisé dans l’application." : "Aucun risque connu dans la zone visible.")
                        .font(.subheadline)
                        .foregroundStyle(TGColor.muted)
                        .tgCard()
                        .padding(20)
                } else {
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 10) {
                            Text("Signaux dans la zone visible").font(.title3.bold())
                            ForEach(displayedRisks) { risk in
                                Button { selected = risk } label: {
                                    HStack {
                                        Text(risk.severityLabel.capitalized)
                                            .font(.caption.bold())
                                            .foregroundStyle(TGColor.coral)
                                        VStack(alignment: .leading) {
                                            Text(risk.name).font(.subheadline.bold())
                                            Text(risk.category).font(.caption).foregroundStyle(TGColor.teal)
                                            Text(risk.summary).font(.caption).foregroundStyle(TGColor.muted).lineLimit(2)
                                        }
                                        Spacer()
                                        Image(systemName: "chevron.right").foregroundStyle(TGColor.muted)
                                    }
                                    .foregroundStyle(TGColor.ink)
                                    .padding(12)
                                    .background(.white)
                                    .clipShape(RoundedRectangle(cornerRadius: 16))
                                }
                            }
                        }
                        .padding(20)
                    }
                }
            }
            .background(TGColor.ivory)
            .navigationTitle("")
            .toolbar(.hidden, for: .navigationBar)
            .navigationBarHidden(true)
            .onAppear { store.location.refresh(); centerInitiallyIfNeeded() }
            .onChange(of: store.location.lastUpdated) { _, _ in centerInitiallyIfNeeded() }
            .onDisappear { positionTask?.cancel(); viewportTask?.cancel() }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
            .fullScreenCover(isPresented: $showFullScreen) { FullScreenRiskMapView(region: $region, selected: $selected) }
        }
    }
}

struct FullScreenRiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @Environment(\.dismiss) private var dismiss
    @Binding var region: MKCoordinateRegion
    @Binding var selected: RiskPlace?
    private var displayedRisks: [RiskPlace] { RiskPlace.inViewport(region, risks: store.risks) }
    private func recenter() { if store.location.isUsingCachedLocation { store.location.refresh(); return }; guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }; region.center = coordinate }
    private func zoom(by factor: Double) { region.span = MKCoordinateSpan(latitudeDelta: min(max(region.span.latitudeDelta * factor, 0.001), 180), longitudeDelta: min(max(region.span.longitudeDelta * factor, 0.001), 360)) }
    var body: some View {
        NavigationStack {
            Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in
                MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) {
                    Button { selected = risk } label: { Image(systemName: "circle.fill").frame(width: 44, height: 44).foregroundStyle(.red).padding(10).background(.white).clipShape(Circle()) }
                }
            }
            .mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }
            .toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View {
    let risk: RiskPlace
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal)
                Text(risk.name).font(.title.bold())
                Text("Risque : \(risk.severityLabel.capitalized)").font(.headline)
                Text(risk.reliabilityLabel).foregroundStyle(TGColor.teal)
                Text(risk.summary).foregroundStyle(TGColor.muted)
                Text("Précision géographique : \(risk.locationPrecision == .point ? "point" : risk.locationPrecision == .neighborhood ? "quartier" : risk.locationPrecision == .city ? "ville" : "pays")").font(.caption).foregroundStyle(TGColor.muted)
                Text(risk.source).font(.caption).foregroundStyle(TGColor.muted)
                Text(risk.freshnessLabel).font(.caption).foregroundStyle(TGColor.muted)
                ForEach(risk.signals, id: \.self) { Text("• \($0)") }
            }
            .padding(24)
        }
        .presentationDetents([.medium])
    }
}
''',
'ScannerView.swift': r'''import CoreImage
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
        var currencyCounts: [String: Int] = [:]; var totalCurrency = ""; var totalPriority = -1
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
                if !detectedCurrency.isEmpty { currencyCounts[detectedCurrency.uppercased(), default: 0] += 1 }
                result.amounts.append(value)
                let isAmountDue = lower.range(of: #"\\b(amount due|à payer|a payer|due)\\b"#, options: .regularExpression) != nil
                let isGrandTotal = lower.range(of: #"\\b(grand total|total général|total general)\\b"#, options: .regularExpression) != nil
                let isTotal = lower.range(of: #"\\b(total)\\b"#, options: .regularExpression) != nil
                let totalRank = isAmountDue ? 4 : isGrandTotal ? 3 : isTotal ? 2 : 0
                let isSubtotal = lower.range(of: #"\\b(subtotal|sous[- ]?total)\\b"#, options: .regularExpression) != nil
                let isTax = lower.range(of: #"\\b(taxe?|tva|vat)\\b"#, options: .regularExpression) != nil
                let isService = lower.range(of: #"\\b(service|tip|service charge|frais|commission|surcharge|supplement)\\b"#, options: .regularExpression) != nil
                let looksNonPrice = lower.range(of: #"\\b(date|table|ticket|receipt|facture|invoice|ref|no\\.?|n[°º])\\b"#, options: .regularExpression) != nil
                if totalRank > 0 { if totalRank >= totalPriority { result.total = value; totalPriority = totalRank; totalCurrency = detectedCurrency } } else if isSubtotal { result.subtotal = value } else if isTax { result.tax = value } else if isService { result.service = value } else if !looksNonPrice { result.itemAmounts.append(value) }
            }
        }
        if !totalCurrency.isEmpty { result.currency = totalCurrency.uppercased() } else if let dominant = currencyCounts.max(by: { $0.value < $1.value })?.key { result.currency = dominant }
        return result
    }
}

enum OCRAssessment: Equatable {
    case coherent, unusual, abusive, undetermined
    var title: String { switch self { case .coherent: return "Total mathématiquement cohérent"; case .unusual: return "Écart arithmétique à vérifier"; case .abusive: return "Prix potentiellement abusif"; case .undetermined: return "Impossible à déterminer" } }
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
    @State private var analysisTask: Task<Void, Never>?
    @State private var analysisGeneration = 0
    private func formatted(_ value: Double) -> String { String(format: "%.2f", value) }
    @ViewBuilder private var structuredSummaryView: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("Lecture structurée").font(.subheadline.bold())
            if !summary.itemAmounts.isEmpty { Text(verbatim: "Articles détectés : " + formatted(summary.itemAmounts.reduce(0, +)) + " " + summary.currency) }
            if let subtotal = summary.subtotal { Text(verbatim: "Sous-total indiqué : " + formatted(subtotal) + " " + summary.currency) }
            if let tax = summary.tax { Text(verbatim: "Taxes : " + formatted(tax) + " " + summary.currency) }
            if let service = summary.service { Text(verbatim: "Service : " + formatted(service) + " " + summary.currency) }
            if let total = summary.total { Text(verbatim: "Total détecté : " + formatted(total) + " " + summary.currency).fontWeight(.bold) }
            if let calculated = summary.calculatedTotal {
                if let difference = summary.difference {
                    let coherent = abs(difference) <= 0.05
                    Text(verbatim: (coherent ? "Total cohérent avec les lignes détectées : " : "Écart arithmétique à vérifier : ") + formatted(coherent ? calculated : difference) + " " + summary.currency).foregroundStyle(coherent ? .green : .red).font(.footnote.bold())
                }
            }
            Text("Résultat limité au document : le total peut être mathématiquement cohérent sans être un prix juste. Aucune comparaison FairPrice officielle n’est disponible sans source locale autorisée.").font(.caption).foregroundStyle(TGColor.muted)
        }
    }

    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 18) {
            Text("CONTRÔLE INTELLIGENT").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted)
            Text("Scanner avant de payer").font(.largeTitle.bold())
            Text("Cadrez un menu, une addition ou un billet. L’analyse est locale et indicative : aucune conclusion officielle n’est inventée.").foregroundStyle(TGColor.muted)
            Button { showingCamera = true } label: { Label("Prendre une photo", systemImage: "camera.fill").font(.headline).foregroundStyle(.white).frame(maxWidth: .infinity).padding().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 16)) }
            PhotosPicker(selection: $selectedItem, matching: .images) { Label("Choisir une photo", systemImage: "photo").font(.headline).foregroundStyle(TGColor.ink).frame(maxWidth: .infinity).padding().background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) }.onChange(of: selectedItem) { _, item in analysisTask?.cancel(); analysisTask = Task { await analyze(item) } }
            if isAnalyzing { ProgressView("Analyse locale du document…").padding(.vertical) }
            if !recognizedLines.isEmpty { VStack(alignment: .leading, spacing: 10) {
                let assessment = summary.assessment(suspectLines: suspectLines)
                Label(assessment.title, systemImage: assessment.icon).font(.headline).foregroundStyle(assessment == .coherent ? .green : assessment == .abusive ? .red : assessment == .unusual ? TGColor.amber : TGColor.muted)
                ForEach(recognizedLines, id: \.self) { line in Text(line).font(.body.weight(suspectLines.contains(line) ? .semibold : .regular)).foregroundStyle(suspectLines.contains(line) ? .red : TGColor.ink).padding(.vertical, 3) }
                if !suspectLines.isEmpty { Text("Vérifiez les frais, taxes, commissions et suppléments avant de payer.").font(.footnote).foregroundStyle(.red) }
                if summary.hasData { structuredSummaryView.padding(.top, 8) }
            }.tgCard() } else if !isAnalyzing { VStack(alignment: .leading, spacing: 8) { Label("Aucun document analysé", systemImage: "viewfinder").font(.headline); Text("Prenez une photo ou choisissez une image pour lancer la détection du texte.").font(.subheadline).foregroundStyle(TGColor.muted) }.tgCard() }
            Label(store.network.isChecking ? "Vérification du réseau…" : store.network.isOnline ? "En ligne · OCR local disponible" : "Hors ligne · OCR local disponible", systemImage: store.network.isOnline ? "wifi" : "wifi.slash").font(.footnote).foregroundStyle(TGColor.muted).padding(.top, 8)
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).sheet(isPresented: $showingCamera) { CameraPicker { image in Task { await recognize(image) } } } }
    }
    @MainActor private func analyze(_ item: PhotosPickerItem?) async { guard let item else { return }; defer { selectedItem = nil }; do { guard let data = try await item.loadTransferable(type: Data.self), let image = UIImage(data: data) else { recognizedLines = ["Image impossible à charger."]; return }; await recognize(image) } catch { recognizedLines = ["La photo n’a pas pu être lue. Choisissez une autre image et réessayez."] } }
    @MainActor private func recognize(_ image: UIImage) async {
        analysisGeneration += 1; let generation = analysisGeneration
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
        guard generation == analysisGeneration, !Task.isCancelled else { return }
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
    private static let ciContext = CIContext()
    static func prepareImage(_ image: UIImage) -> UIImage? {
        let maxWidth: CGFloat = 2200; let scale = min(1, maxWidth / max(image.size.width, 1)); let size = CGSize(width: image.size.width * scale, height: image.size.height * scale)
        let renderer = UIGraphicsImageRenderer(size: size); let normalized = renderer.image { _ in image.draw(in: CGRect(origin: .zero, size: size)) }
        guard let input = CIImage(image: normalized), let filter = CIFilter(name: "CIColorControls") else { return normalized }
        filter.setValue(input, forKey: kCIInputImageKey); filter.setValue(1.15, forKey: kCIInputContrastKey); filter.setValue(0.05, forKey: kCIInputBrightnessKey)
        guard let output = filter.outputImage, let cg = ciContext.createCGImage(output, from: output.extent) else { return normalized }
        return UIImage(cgImage: cg, scale: normalized.scale, orientation: .up)
    }
}

struct CameraPicker: UIViewControllerRepresentable {
    let onImage: (UIImage) -> Void

    func makeCoordinator() -> Coordinator { Coordinator(onImage: onImage) }

    func makeUIViewController(context: Context) -> UIViewController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            picker.sourceType = .photoLibrary
            return picker
        }
        picker.sourceType = .camera
        picker.allowsEditing = false
        return picker
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}

    final class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let onImage: (UIImage) -> Void
        init(onImage: @escaping (UIImage) -> Void) { self.onImage = onImage }
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage { onImage(image) }
            picker.dismiss(animated: true)
        }
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) { picker.dismiss(animated: true) }
    }
}''',
'SafetyView.swift': r'''import CoreLocation
import SwiftUI
import UIKit

struct SafetyView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var phraseIndex = 0
    @State private var callError = false
    private var emergencyNumber: String {
        let region = store.location.countryCode.uppercased()
        if ["US", "CA"].contains(region) { return "911" }
        if region == "GB" { return "999" }
        if region == "AU" { return "000" }
        if region == "JP" { return "110" }
        if ["CN", "KR"].contains(region) { return "112" }
        return "112"
    }
    private var alertsBinding: Binding<Bool> { Binding(get: { store.location.proximityAlertsEnabled }, set: { store.location.setProximityAlerts($0) }) }
    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 16) { HStack { VStack(alignment: .leading) { Text("PROTECTION ET RÉFÉRENCES").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Sécurité").font(.largeTitle.bold()) }; Spacer(); Label(store.protectionStatusLabel, systemImage: store.protectionStatusLabel == "Protection active" ? "checkmark.shield.fill" : "exclamationmark.shield").font(.caption.bold()).foregroundStyle(store.protectionStatusLabel == "Protection active" ? .green : TGColor.amber) }
            VStack(alignment: .leading, spacing: 12) { Label("BESOIN D’AIDE ?", systemImage: "shield.fill").font(.caption.weight(.heavy)).foregroundStyle(.white.opacity(0.85)); Text("Gardez vos phrases prêtes.").font(.title2.bold()).foregroundStyle(.white); Text("Affichez une phrase locale sans chercher dans vos réglages.").foregroundStyle(.white.opacity(0.85)); HStack { Button { phraseIndex = (phraseIndex + 1) % sampleSOS.count } label: { Label("Phrase locale", systemImage: "speaker.wave.2.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral); Button { guard let url = URL(string: "tel://\(emergencyNumber)"), UIApplication.shared.canOpenURL(url) else { callError = true; return }; UIApplication.shared.open(url) { success in if !success { Task { @MainActor in callError = true } } } } label: { Label("Secours \(emergencyNumber)", systemImage: "phone.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral) } }.padding(18).frame(maxWidth: .infinity, alignment: .leading).background(TGColor.coral).clipShape(RoundedRectangle(cornerRadius: 22))
            VStack(alignment: .leading, spacing: 8) { HStack { Text(sampleSOS[phraseIndex].language).font(.caption.bold()).foregroundStyle(TGColor.teal); Spacer(); Text(store.network.isOnline ? "En ligne" : "Hors ligne").font(.caption.bold()).foregroundStyle(TGColor.muted) }; Text(sampleSOS[phraseIndex].local).font(.title3.bold()); Text(sampleSOS[phraseIndex].translation).foregroundStyle(TGColor.muted) }.tgCard()
            Text("Réglages de protection").font(.title3.bold()); Toggle("Alertes de proximité", isOn: alertsBinding).tint(TGColor.teal).disabled(store.risks.isEmpty).tgCard(); Text(store.risks.isEmpty ? "Aucune source géolocalisée fiable · alertes indisponibles" : store.location.proximityAlertsEnabled ? (store.location.notificationPermission != .authorized ? "Alertes indisponibles · notifications désactivées" : store.location.monitoringActive ? "Alertes actives · régions iOS surveillées" : "Alertes prêtes · aucun risque pertinent à proximité") : "Alertes désactivées").font(.caption.bold()).foregroundStyle(store.location.monitoringActive ? TGColor.teal : TGColor.muted); Text(store.riskDataFreshnessLabel).font(.caption.bold()).foregroundStyle(store.riskDataIsStale ? TGColor.amber : TGColor.muted); Text("Les alertes utilisent la surveillance de régions iOS et nécessitent les autorisations de localisation et de notifications. Aucune alerte locale n’est activée sans une source géolocalisée autorisée. Les sources officielles générales sont consultables ci-dessous.").font(.caption).foregroundStyle(TGColor.muted); HStack { Image(systemName: store.network.isOnline ? "wifi" : "wifi.slash").foregroundStyle(store.network.isOnline ? .green : TGColor.amber); VStack(alignment: .leading) { Text("Mode hors ligne automatique").font(.subheadline.bold()); Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Connexion active · données locales prêtes" : "Aucune connexion · données locales utilisées").font(.caption).foregroundStyle(TGColor.muted) } }.tgCard()
            Text("Références de prix · \(store.location.city)").font(.title3.bold()); if prices(for: store.location.city).isEmpty { Text("Cette fonctionnalité n’est pas disponible pour cette ville sans source FairPrice autorisée. TravelGuard ne fabrique pas de tarif et ne convertit pas un prix sans devise et source autorisées.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() } else { ForEach(prices(for: store.location.city)) { price in HStack { Text(price.label).bold(); Spacer(); Text(price.value) }.tgCard() } }; Text("Sources officielles").font(.title3.bold()); ForEach(officialSources) { source in Button { if let url = URL(string: source.url) { UIApplication.shared.open(url) } } label: { HStack { Image(systemName: "checkmark.seal").foregroundStyle(TGColor.teal); VStack(alignment: .leading) { Text(source.title).font(.subheadline.bold()); Text(source.scope).font(.caption).foregroundStyle(TGColor.muted) }; Spacer(); Image(systemName: "arrow.up.right").foregroundStyle(TGColor.muted) }.tgCard() } }
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { if store.risks.isEmpty { store.location.setProximityAlerts(false) } else if store.location.proximityAlertsEnabled { store.location.restoreProximityAlertsIfAuthorized() } }.alert("Appel indisponible", isPresented: $callError) { Button("OK", role: .cancel) {} } message: { Text("Ce téléphone ne peut pas lancer automatiquement l’appel. Composez le numéro d’urgence local manuellement.") } }
    }
}
''',
'Info.plist': r'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleIdentifier</key><string>$(PRODUCT_BUNDLE_IDENTIFIER)</string>
<key>CFBundleExecutable</key><string>$(EXECUTABLE_NAME)</string>
<key>CFBundleDisplayName</key><string>TravelGuard</string>
<key>CFBundleName</key><string>TravelGuard</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSRequiresIPhoneOS</key><true/>
<key>RiskFeedURL</key><string></string>
<key>RiskFeedAllowedHost</key><string></string>
<key>NSCameraUsageDescription</key><string>TravelGuard utilise la caméra pour scanner les menus, additions et billets.</string>
<key>NSLocationWhenInUseUsageDescription</key><string>TravelGuard utilise votre position pour afficher les risques et tarifs autour de vous.</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key><string>TravelGuard peut surveiller les zones signalées en arrière-plan uniquement si vous activez explicitement les alertes de proximité.</string>
<key>NSPhotoLibraryUsageDescription</key><string>TravelGuard utilise vos photos pour analyser un menu ou un billet.</string>
<key>UILaunchScreen</key><dict><key>UIColorName</key><string>LaunchBackground</string></dict>
</dict></plist>
''',
'Assets.xcassets/Contents.json': '{"info":{"author":"xcode","version":1}}',
'Assets.xcassets/AppIcon.appiconset/Contents.json': '{"images":[{"filename":"Icon-1024.png","idiom":"universal","platform":"ios","size":"1024x1024"}],"info":{"author":"xcode","version":1}}',
'Assets.xcassets/LaunchBackground.colorset/Contents.json': '{"colors":[{"idiom":"universal","color":{"color-space":"srgb","components":{"alpha":"1.000","blue":"0.930","green":"0.970","red":"0.980"}}}],"info":{"author":"xcode","version":1}}',
}
for rel, content in files.items():
    path = APP / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
source_icon = Path('/home/ubuntu/travelguard/assets/images/icon.png')
if source_icon.exists():
    shutil.copyfile(source_icon, APP / 'Assets.xcassets' / 'AppIcon.appiconset' / 'Icon-1024.png')

# Minimal Xcode project generated with deterministic UUIDs.
swift_files = [p.name for p in APP.glob('*.swift')]
ids = {
    'project':'A00000000000000000000001','target':'A00000000000000000000002','sources':'A00000000000000000000003','resources':'A00000000000000000000004','frameworks':'A00000000000000000000005','products':'A00000000000000000000006','appref':'A00000000000000000000007','mainGroup':'A00000000000000000000008','appGroup':'A00000000000000000000009','configProjDebug':'A00000000000000000000010','configProjRelease':'A00000000000000000000011','configTargetDebug':'A00000000000000000000012','configTargetRelease':'A00000000000000000000013','projConfigList':'A00000000000000000000014','targetConfigList':'A00000000000000000000015','assetRef':'A00000000000000000000016','assetBuild':'A00000000000000000000017','plistRef':'A00000000000000000000018','plistBuild':'A00000000000000000000019'
}
for i, name in enumerate(swift_files, start=20):
    ids[name] = f'A000000000000000000000{i:02d}'
    ids[name+'build'] = f'A000000000000000000001{i:02d}'
source_builds = ',\n'.join(f'\t\t{ids[name+"build"]} /* {name} in Sources */' for name in swift_files)
source_refs = ',\n'.join(f'\t\t\t{ids[name]} /* {name} */' for name in swift_files)
source_file_objs = '\n'.join(f'\t\t{ids[name+"build"]} /* {name} in Sources */ = {{isa = PBXBuildFile; fileRef = {ids[name]} /* {name} */; }};' for name in swift_files)
file_refs = '\n'.join(f'\t\t{ids[name]} /* {name} */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = {name}; sourceTree = "<group>"; }};' for name in swift_files)
pbx = f'''// !$*UTF8*$!
{{
 archiveVersion = 1;
 objectVersion = 56;
 objects = {{
{source_file_objs}
\t\t{ids['assetBuild']} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {ids['assetRef']} /* Assets.xcassets */; }};
\t\t{ids['plistBuild']} /* Info.plist in Resources */ = {{isa = PBXBuildFile; fileRef = {ids['plistRef']} /* Info.plist */; }};
{file_refs}
\t\t{ids['assetRef']} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
\t\t{ids['plistRef']} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
\t\t{ids['appref']} /* TravelGuard.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = TravelGuard.app; sourceTree = BUILT_PRODUCTS_DIR; }};
\t\t{ids['project']} /* Project object */ = {{isa = PBXProject; attributes = {{ LastUpgradeCheck = 1600; ORGANIZATIONNAME = TravelGuard; TargetAttributes = {{ {ids['target']} = {{ CreatedOnToolsVersion = 16.0; }}; }}; }}; buildConfigurationList = {ids['projConfigList']} /* Build configuration list for PBXProject */; compatibilityVersion = "Xcode 14.0"; developmentRegion = en; hasScannedForEncodings = 0; knownRegions = (en, fr, Base); mainGroup = {ids['mainGroup']}; productRefGroup = {ids['products']}; projectDirPath = ""; projectRoot = ""; targets = ({ids['target']}); }};
\t\t{ids['mainGroup']} /* Main group */ = {{isa = PBXGroup; children = ({ids['appGroup']}, {ids['products']}); sourceTree = "<group>"; }};
\t\t{ids['appGroup']} /* TravelGuard group */ = {{isa = PBXGroup; children = ({source_refs}, {ids['assetRef']} /* Assets.xcassets */, {ids['plistRef']} /* Info.plist */); path = TravelGuard; sourceTree = "<group>"; }};
\t\t{ids['products']} /* Products */ = {{isa = PBXGroup; children = ({ids['appref']}); name = Products; sourceTree = "<group>"; }};
\t\t{ids['target']} /* TravelGuard target */ = {{isa = PBXNativeTarget; buildConfigurationList = {ids['targetConfigList']} /* Build configuration list for PBXNativeTarget "TravelGuard" */; buildPhases = ({ids['sources']}, {ids['frameworks']}, {ids['resources']}); buildRules = (); dependencies = (); name = TravelGuard; productName = TravelGuard; productReference = {ids['appref']}; productType = "com.apple.product-type.application"; }};
\t\t{ids['sources']} /* Sources */ = {{isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = ({source_builds}); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{ids['frameworks']} /* Frameworks */ = {{isa = PBXFrameworksBuildPhase; buildActionMask = 2147483647; files = (); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{ids['resources']} /* Resources */ = {{isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = ({ids['assetBuild']}); runOnlyForDeploymentPostprocessing = 0; }};
\t\t{ids['projConfigList']} = {{isa = XCConfigurationList; buildConfigurations = ({ids['configProjDebug']}, {ids['configProjRelease']}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
\t\t{ids['targetConfigList']} = {{isa = XCConfigurationList; buildConfigurations = ({ids['configTargetDebug']}, {ids['configTargetRelease']}); defaultConfigurationIsVisible = 0; defaultConfigurationName = Release; }};
\t\t{ids['configProjDebug']} /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{ ALWAYS_SEARCH_USER_PATHS = NO; SWIFT_VERSION = 5.0; }}; name = Debug; }};
\t\t{ids['configProjRelease']} /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{ ALWAYS_SEARCH_USER_PATHS = NO; SWIFT_VERSION = 5.0; }}; name = Release; }};
\t\t{ids['configTargetDebug']} /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{ ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; DEVELOPMENT_TEAM = ""; INFOPLIST_FILE = TravelGuard/Info.plist; IPHONEOS_DEPLOYMENT_TARGET = 17.0; PRODUCT_BUNDLE_IDENTIFIER = com.daisheroique.travelguard; PRODUCT_NAME = TravelGuard; SWIFT_EMIT_LOC_STRINGS = YES; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = "1"; }}; name = Debug; }};
\t\t{ids['configTargetRelease']} /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{ ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; CODE_SIGN_STYLE = Automatic; CURRENT_PROJECT_VERSION = 1; DEVELOPMENT_TEAM = ""; INFOPLIST_FILE = TravelGuard/Info.plist; IPHONEOS_DEPLOYMENT_TARGET = 17.0; PRODUCT_BUNDLE_IDENTIFIER = com.daisheroique.travelguard; PRODUCT_NAME = TravelGuard; SWIFT_OPTIMIZATION_LEVEL = "-O"; SWIFT_EMIT_LOC_STRINGS = YES; SWIFT_VERSION = 5.0; TARGETED_DEVICE_FAMILY = "1"; }}; name = Release; }};
 }}
 rootObject = {ids['project']} /* Project object */;
}}
'''
(PROJ / 'project.pbxproj').write_text(pbx)
(PROJ / 'project.xcworkspace' / 'contents.xcworkspacedata').write_text('<?xml version="1.0" encoding="UTF-8"?><Workspace version="1.0"><FileRef location="group:TravelGuard.xcodeproj"/></Workspace>')
scheme_dir = PROJ / 'xcshareddata' / 'xcschemes'
scheme_dir.mkdir(parents=True, exist_ok=True)
(scheme_dir / 'TravelGuard.xcscheme').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1600" version="1.7">
  <BuildAction parallelizeBuildables="YES" buildImplicitDependencies="YES"><BuildActionEntries><BuildActionEntry buildForTesting="YES" buildForRunning="YES" buildForProfiling="YES" buildForArchiving="YES" buildForAnalyzing="YES" message="YES" runPostActionsImmediately="YES"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{ids['target']}" BuildableName="TravelGuard.app" BlueprintName="TravelGuard" ReferencedContainer="container:TravelGuard.xcodeproj"><BuildableName>TravelGuard.app</BuildableName></BuildableReference></BuildActionEntry></BuildActionEntries></BuildAction>
  <TestAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES"/>
  <LaunchAction buildConfiguration="Release" selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier="Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle="0" useCustomWorkingDirectory="NO" ignoresPersistentStateOnLaunch="NO" debugDocumentVersioning="YES" debugServiceExtension="internal" allowLocationSimulation="YES"><BuildableProductRunnable runnableDebuggingMode="0"><BuildableReference BuildableIdentifier="primary" BlueprintIdentifier="{ids['target']}" BuildableName="TravelGuard.app" BlueprintName="TravelGuard" ReferencedContainer="container:TravelGuard.xcodeproj"/></BuildableProductRunnable></LaunchAction>
  <ProfileAction buildConfiguration="Release" shouldUseLaunchSchemeArgsEnv="YES" savedToolIdentifier="" useCustomWorkingDirectory="NO" debugDocumentVersioning="YES"/>
  <AnalyzeAction buildConfiguration="Debug"/>
  <ArchiveAction buildConfiguration="Release" revealArchiveInOrganizer="YES"/>
</Scheme>
''')
(ROOT / 'README.md').write_text('''# TravelGuard iOS\n\nTravelGuard est une application iOS native SwiftUI. Le projet canonique est `native-package/TravelGuard.xcodeproj` et ne dépend ni d’Expo, ni de Metro, ni de Node, ni de CocoaPods à l’exécution.\n\n## Ouvrir sur Mac\n\n```bash\ngit clone https://github.com/dais-heroique/travelguard.git\ncd travelguard\nopen native-package/TravelGuard.xcodeproj\n```\n\nDans Xcode, sélectionnez votre Team, votre iPhone et le schéma `TravelGuard` en configuration Release. La compilation et le test appareil final doivent être exécutés sur macOS avec Xcode.\n\n## Fonctionnalités natives\n\nLe paquet comprend l’onboarding, la demande de localisation, le suivi GPS avec filtrage de précision, MapKit avec zoom tactile, le scanner Vision OCR depuis caméra ou Photos, l’extraction structurée des montants, le mode hors ligne, les phrases SOS et la persistance locale.\n\nAucun risque géolocalisé ni tarif n’est affiché comme officiel sans source autorisée et traçable. Lorsque les sources ne sont pas disponibles, l’interface affiche explicitement l’absence de données et propose des liens institutionnels généraux. Les alertes en arrière-plan nécessitent une source de risque fiable, l’autorisation iOS `Toujours` et les notifications ; elles restent désactivées tant qu’aucune donnée sourcée n’est intégrée.\n\n## Vérifications reproductibles\n\n```bash\npython3 -m py_compile scripts/*.py\npython3 scripts/generate_native_ios.py\npython3 scripts/rewrite_native_pbx.py\npython3 scripts/validate_xcode_project.py\npython3 scripts/validate_native_quality.py\nunzip -tq TravelGuard-Xcode-FIXED.zip\n```\n\nVoir `NATIVE_TEST_MATRIX.md` pour la matrice Mac/iPhone. Les dossiers Expo/Web sont historiques ; pour l’application iPhone, utilisez exclusivement `native-package/TravelGuard.xcodeproj`.\n''')
print(f'Generated {ROOT}')
