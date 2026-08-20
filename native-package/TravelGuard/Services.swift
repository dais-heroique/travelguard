import Combine
import CoreLocation
import Foundation
import Network
import UserNotifications

@MainActor
final class LocationService: NSObject, ObservableObject, CLLocationManagerDelegate {
    @Published private(set) var authorization: CLAuthorizationStatus = .notDetermined
    @Published private(set) var servicesEnabled = true
    @Published private(set) var coordinate: CLLocationCoordinate2D?
    @Published private(set) var accuracy: CLLocationAccuracy?
    @Published private(set) var city = "Localisation requise"
    @Published private(set) var country = ""
    @Published private(set) var errorMessage: String?
    @Published private(set) var lastUpdated: Date?
    private let manager = CLLocationManager()
    private let geocoder = CLGeocoder()
    private let cacheLifetime: TimeInterval = 24 * 60 * 60

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 25
        authorization = manager.authorizationStatus
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        restoreFreshCache()
        if hasPermission { manager.startUpdatingLocation() }
        if UserDefaults.standard.bool(forKey: "alertsEnabled") { setProximityAlerts(true) }
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
        guard servicesEnabled else { errorMessage = "Activez la localisation dans Réglages pour utiliser les risques à proximité."; return }
        if hasPermission { manager.startUpdatingLocation() } else { manager.requestWhenInUseAuthorization() }
    }

    func refresh() {
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        guard servicesEnabled, hasPermission else { return }
        manager.startUpdatingLocation()
        manager.requestLocation()
    }

    func setProximityAlerts(_ enabled: Bool) {
        if !enabled {
            sampleRisks.forEach { manager.stopMonitoring(for: CLCircularRegion(center: CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude), radius: 100, identifier: $0.id)) }
            return
        }
        Task {
            let granted = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])
            guard granted == true, hasPermission else { return }
            for risk in sampleRisks {
                let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: 100, identifier: risk.id)
                region.notifyOnEntry = true
                manager.startMonitoring(for: region)
            }
        }
    }

    private func restoreFreshCache() {
        guard let latitude = UserDefaults.standard.object(forKey: "lastLatitude") as? Double,
              let longitude = UserDefaults.standard.object(forKey: "lastLongitude") as? Double,
              let timestamp = UserDefaults.standard.object(forKey: "lastLocationTimestamp") as? Date,
              Date().timeIntervalSince(timestamp) <= cacheLifetime else { return }
        coordinate = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        city = UserDefaults.standard.string(forKey: "lastCity") ?? "Dernière position connue"
        country = UserDefaults.standard.string(forKey: "lastCountry") ?? ""
        lastUpdated = timestamp
        accuracy = UserDefaults.standard.object(forKey: "lastLocationAccuracy") as? Double
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorization = manager.authorizationStatus
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        if hasPermission { manager.startUpdatingLocation() } else if permissionDenied { errorMessage = "Autorisation refusée. Vous pouvez l’activer dans Réglages." }
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let location = locations.last, location.horizontalAccuracy >= 0 else { return }
        coordinate = location.coordinate
        accuracy = location.horizontalAccuracy
        lastUpdated = Date()
        errorMessage = nil
        UserDefaults.standard.set(location.coordinate.latitude, forKey: "lastLatitude")
        UserDefaults.standard.set(location.coordinate.longitude, forKey: "lastLongitude")
        UserDefaults.standard.set(location.horizontalAccuracy, forKey: "lastLocationAccuracy")
        UserDefaults.standard.set(Date(), forKey: "lastLocationTimestamp")
        geocoder.reverseGeocodeLocation(location) { [weak self] places, _ in
            guard let self, let place = places?.first else { return }
            Task { @MainActor in
                self.city = place.locality ?? place.subAdministrativeArea ?? place.administrativeArea ?? "Position détectée"
                self.country = place.country ?? ""
                UserDefaults.standard.set(self.city, forKey: "lastCity")
                UserDefaults.standard.set(self.country, forKey: "lastCountry")
            }
        }
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        errorMessage = "Position indisponible pour le moment. Vérifiez le signal GPS et réessayez."
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

    func completeOnboarding(profile: String, priorities: Set<String>) {
        travelerProfile = profile
        self.priorities = priorities
        UserDefaults.standard.set(profile, forKey: "travelerProfile")
        UserDefaults.standard.set(Array(priorities), forKey: "priorities")
        UserDefaults.standard.set(true, forKey: "onboardingComplete")
        onboardingComplete = true
    }
}
