import Combine
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
