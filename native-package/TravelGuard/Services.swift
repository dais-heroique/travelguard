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
    @Published private(set) var lastUpdated: Date?
    @Published private(set) var notificationPermission: UNAuthorizationStatus = .notDetermined
    private let manager = CLLocationManager()
    private let geocoder = CLGeocoder()
    private let cacheLifetime: TimeInterval = 24 * 60 * 60
    private var lastGeocodeLocation: CLLocation?
    private var hasFreshLocationForAlerts = false
    private var monitoredRisks: [RiskPlace] = trustedRisks
    private var lastRegionRefreshLocation: CLLocation?
    private var waitingForAlwaysAuthorization = false

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
    var locationStatus: String {
        if !servicesEnabled { return "Services de localisation désactivés" }
        if permissionDenied { return "Autorisation de localisation refusée" }
        if coordinate == nil { return "Localisation en cours…" }
        if let accuracy { return "Précision ±\(Int(max(0, accuracy))) m" }
        return "Position détectée"
    }

    func requestPermission() {
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        guard servicesEnabled else { errorMessage = "Activez la localisation dans Réglages pour utiliser les risques à proximité."; openSettings(); return }
                if hasPermission {
            manager.requestLocation()
            if authorization == .authorizedAlways && UserDefaults.standard.bool(forKey: "alertsEnabled") && notificationPermission == .authorized { waitingForAlwaysAuthorization = false }
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
            return
        }
        proximityAlertsEnabled = true
        monitoringActive = false
        waitingForAlwaysAuthorization = authorization != .authorizedAlways
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
                if self.authorization == .authorizedAlways { self.waitingForAlwaysAuthorization = false; self.manager.requestLocation() }
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
                if settings.authorizationStatus == .authorized && self.authorization == .authorizedAlways { self.waitingForAlwaysAuthorization = false; self.manager.requestLocation() }
            }
        }
    }

    func refreshMonitoredRegions() {
        guard hasFreshLocationForAlerts else { return }
        monitorRiskRegions()
    }

    /// Called by a future API/offline sync after replacing the authoritative risk set.
    func updateRisks(_ risks: [RiskPlace]) {
        monitoredRisks = risks
        if risks.isEmpty { proximityAlertsEnabled = false; monitoringActive = false; UserDefaults.standard.set(false, forKey: "alertsEnabled"); manager.monitoredRegions.forEach { manager.stopMonitoring(for: $0) }; return }
        if UserDefaults.standard.bool(forKey: "alertsEnabled") && authorization == .authorizedAlways {
            proximityAlertsEnabled = true
            manager.requestLocation()
        }
    }

    private func monitorRiskRegions() {
        guard authorization == .authorizedAlways, proximityAlertsEnabled, hasFreshLocationForAlerts, (accuracy ?? 999) <= 200, let current = coordinate else { monitoringActive = false; return }
        let nearby = monitoredRisks
            .compactMap { risk -> (risk: RiskPlace, score: Double)? in
                guard let distance = risk.distance(from: current), distance <= 10000 else { return nil }
                let distanceScore = max(0, 1 - (distance / 10000))
                let severityScore = min(1, max(0, Double(risk.score) / 100))
                let confidenceScore = min(1, max(0, Double(risk.confidenceScore) / 100))
                let monitoringScore = distanceScore * 0.5 + severityScore * 0.3 + confidenceScore * 0.2
                return (risk, monitoringScore)
            }
            .sorted { $0.score > $1.score }
            .prefix(20)
        let desiredIDs = Set(nearby.map { $0.risk.id })
        manager.monitoredRegions.filter { !desiredIDs.contains($0.identifier) }.forEach { manager.stopMonitoring(for: $0) }
        for entry in nearby {
            let risk = entry.risk
            guard !manager.monitoredRegions.contains(where: { $0.identifier == risk.id }) else { continue }
            let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: 250, identifier: risk.id)
            region.notifyOnEntry = true
            manager.startMonitoring(for: region)
        }
        lastRegionRefreshLocation = current
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
            if authorization == .authorizedAlways && UserDefaults.standard.bool(forKey: "alertsEnabled") && notificationPermission == .authorized { waitingForAlwaysAuthorization = false }
        } else if permissionDenied { errorMessage = "Autorisation refusée. Vous pouvez l’activer dans Réglages." }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last, location.horizontalAccuracy >= 0 else { return }
        coordinate = location.coordinate
        accuracy = location.horizontalAccuracy
        lastUpdated = Date()
        hasFreshLocationForAlerts = location.horizontalAccuracy <= 200
        isUsingCachedLocation = false
        errorMessage = location.horizontalAccuracy > 200 ? "Position très imprécise (±\(Int(location.horizontalAccuracy)) m) : distances et alertes approximatives." : location.horizontalAccuracy > 100 ? "Position GPS approximative (±\(Int(location.horizontalAccuracy)) m)." : nil
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
                Task { @MainActor in self?.errorMessage = "Ville indisponible pour le moment ; la position GPS reste utilisable." }
                return
            }
            Task { @MainActor in
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
        let code = (error as? CLError)?.code
        print("[TravelGuard][Location] error=\(String(describing: code)) description=\(error.localizedDescription)")
        if code == .denied { errorMessage = "Autorisation de localisation refusée. Ouvrez Réglages." }
        else if code == .locationUnknown { errorMessage = "Position GPS temporairement indisponible. Réessayez dans quelques instants." }
        else { errorMessage = "Erreur GPS (\(code?.rawValue ?? -1)) : \(error.localizedDescription)" }
        if coordinate == nil { city = "Position indisponible" }
    }

    func locationManager(_ manager: CLLocationManager, didEnterRegion region: CLRegion) {
        let content = UNMutableNotificationContent()
        content.title = "TravelGuard · vigilance"
        content.body = "Vous entrez dans une zone signalée. Vérifiez les prix et conditions avant de payer."
        content.sound = .default
        UNUserNotificationCenter.current().add(UNNotificationRequest(identifier: "risk-\(region.identifier)-\(Date().timeIntervalSince1970)", content: content, trigger: nil))
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
    let location = LocationService()
    let network = NetworkMonitor()
    @Published var selectedTab = 0

    init() {
        onboardingComplete = UserDefaults.standard.bool(forKey: "onboardingComplete")
    }

    func updateRisks(_ risks: [RiskPlace]) { location.updateRisks(risks) }

    func completeOnboarding(profile: String, priorities: Set<String>) {
        travelerProfile = profile
        self.priorities = priorities
        UserDefaults.standard.set(profile, forKey: "travelerProfile")
        UserDefaults.standard.set(Array(priorities), forKey: "priorities")
        UserDefaults.standard.set(true, forKey: "onboardingComplete")
        onboardingComplete = true
    }
}
