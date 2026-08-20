from pathlib import Path
import json
import shutil

ROOT = Path('/home/ubuntu/travelguard/native-package')
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

struct RiskPlace: Identifiable, Hashable {
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

    var confidenceScore: Int {
        let ageDays = max(0, Calendar.current.dateComponents([.day], from: updatedAt, to: Date()).day ?? 0)
        let freshness = max(0, 25 - min(ageDays, 25))
        let reportSignal = min(25, reportCount * 2)
        let sourceSignal = source.contains("démonstration") ? 5 : 20
        return min(100, max(0, (score / 2) + freshness + reportSignal + sourceSignal))
    }

    func formattedDistance(from coordinate: CLLocationCoordinate2D?) -> String {
        guard let meters = distance(from: coordinate) else { return "Distance inconnue" }
        if meters < 1000 { return "\(Int(meters.rounded())) m" }
        return String(format: "%.1f km", meters / 1000).replacingOccurrences(of: ".0 km", with: " km")
    }
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

let demoRisks = [
    RiskPlace(id: "taxi-1", name: "Taxi sans compteur", category: "Taxi", score: 31, summary: "Refus fréquent du compteur et tarif annoncé après la course.", latitude: 48.8584, longitude: 2.2945, signals: ["Pas de compteur visible", "Prix variable selon le client"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 12),
    RiskPlace(id: "exchange-1", name: "Change très défavorable", category: "Change", score: 44, summary: "Taux affiché sans frais réels clairement visibles.", latitude: 48.8606, longitude: 2.3376, signals: ["Commission peu lisible", "Écart au taux de référence"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 8),
    RiskPlace(id: "restaurant-1", name: "Menu touristique", category: "Restaurant", score: 58, summary: "Suppléments signalés sur les terrasses et accompagnements.", latitude: 48.8530, longitude: 2.3499, signals: ["Menu sans prix détaillés", "Service ajouté automatiquement"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 5)
]

// Données de démonstration conservées uniquement pour les tests visuels ; jamais affichées comme locales.
let trustedRisks: [RiskPlace] = []

let samplePrices = [
    FairPrice(id: "coffee", label: "Café", value: "2,50 €", reference: "Repère local indicatif", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate),
    FairPrice(id: "taxi", label: "Course taxi", value: "12–18 €", reference: "Trajet urbain standard", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate),
    FairPrice(id: "museum", label: "Billet attraction", value: "18 €", reference: "Tarif officiel indicatif", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate)
]

func prices(for city: String) -> [FairPrice] {
    samplePrices.filter { $0.city.localizedCaseInsensitiveCompare(city) == .orderedSame && !$0.source.contains("démonstration") }
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
    @Published private(set) var errorMessage: String?
    @Published private(set) var lastUpdated: Date?
    @Published private(set) var notificationPermission: UNAuthorizationStatus = .notDetermined
    private let manager = CLLocationManager()
    private let geocoder = CLGeocoder()
    private let cacheLifetime: TimeInterval = 24 * 60 * 60
    private var lastGeocodeLocation: CLLocation?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyNearestTenMeters
        manager.distanceFilter = 50
        manager.activityType = .otherNavigation
        manager.pausesLocationUpdatesAutomatically = true
        authorization = manager.authorizationStatus
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        restoreFreshCache()
        if hasPermission { manager.startUpdatingLocation() }
        if UserDefaults.standard.bool(forKey: "alertsEnabled") { restoreProximityAlertsIfAuthorized() }
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
        if hasPermission { manager.startUpdatingLocation() } else if permissionDenied { errorMessage = "Autorisation refusée. Ouvrez Réglages → TravelGuard → Localisation."; openSettings() } else { manager.requestWhenInUseAuthorization() }
    }

    private func openSettings() {
        guard let url = URL(string: UIApplication.openSettingsURLString) else { return }
        UIApplication.shared.open(url)
    }

    func refresh() {
        servicesEnabled = CLLocationManager.locationServicesEnabled()
        guard servicesEnabled, hasPermission else { return }
        manager.startUpdatingLocation()
        manager.requestLocation()
    }

    func setProximityAlerts(_ enabled: Bool) {
        UserDefaults.standard.set(enabled, forKey: "alertsEnabled")
        if !enabled {
            trustedRisks.forEach { manager.stopMonitoring(for: CLCircularRegion(center: CLLocationCoordinate2D(latitude: $0.latitude, longitude: $0.longitude), radius: 250, identifier: $0.id)) }
            return
        }
        Task {
            let granted = try? await UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound])
            guard granted == true, hasPermission else { return }
            await MainActor.run { self.monitorRiskRegions() }
        }
    }

    func restoreProximityAlertsIfAuthorized() {
        UNUserNotificationCenter.current().getNotificationSettings { [weak self] settings in
            Task { @MainActor in
                guard let self else { return }
                self.notificationPermission = settings.authorizationStatus
                if settings.authorizationStatus == .authorized && self.hasPermission { self.monitorRiskRegions() }
            }
        }
    }

    private func monitorRiskRegions() {
        for risk in trustedRisks {
            let region = CLCircularRegion(center: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude), radius: 250, identifier: risk.id)
            region.notifyOnEntry = true
            manager.startMonitoring(for: region)
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
        guard location.horizontalAccuracy <= 100 else { errorMessage = "Précision GPS insuffisante (±\(Int(location.horizontalAccuracy)) m). Les risques locaux restent masqués."; accuracy = location.horizontalAccuracy; return }
        coordinate = location.coordinate
        accuracy = location.horizontalAccuracy
        lastUpdated = Date()
        errorMessage = nil
        UserDefaults.standard.set(location.coordinate.latitude, forKey: "lastLatitude")
        UserDefaults.standard.set(location.coordinate.longitude, forKey: "lastLongitude")
        UserDefaults.standard.set(location.horizontalAccuracy, forKey: "lastLocationAccuracy")
        UserDefaults.standard.set(Date(), forKey: "lastLocationTimestamp")
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
        guard let coordinate = store.location.coordinate, (store.location.accuracy ?? 999) <= 100 else { return [] }
        return trustedRisks.filter { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) <= 10000 }.sorted { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) < ($1.distance(from: coordinate) ?? .greatestFiniteMagnitude) }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack { VStack(alignment: .leading, spacing: 4) { Text("TRAVELGUARD").font(.caption.weight(.heavy)).tracking(1.5).foregroundStyle(TGColor.muted); Text("Voyagez l’esprit léger.").font(.system(size: 29, weight: .bold, design: .rounded)).foregroundStyle(TGColor.ink) }; Spacer(); Text("TG").font(.headline).foregroundStyle(.white).frame(width: 42, height: 42).background(TGColor.teal).clipShape(Circle()) }
                    VStack(alignment: .leading, spacing: 12) {
                        Label(store.location.hasPermission && store.location.coordinate != nil ? "PROTECTION ACTIVE" : "LOCALISATION NÉCESSAIRE", systemImage: store.location.hasPermission && store.location.coordinate != nil ? "checkmark.shield.fill" : "location.slash").font(.caption.weight(.heavy)).foregroundStyle(store.location.hasPermission && store.location.coordinate != nil ? TGColor.mint : TGColor.amber)
                        Text(place).font(.title2.bold()).foregroundStyle(.white)
                        HStack(spacing: 14) { Label(store.location.locationStatus, systemImage: "location.fill"); Label(store.network.isOnline ? "En ligne" : "Hors ligne", systemImage: store.network.isOnline ? "wifi" : "wifi.slash") }.font(.caption.weight(.semibold)).foregroundStyle(.white.opacity(0.88))
                        Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Données locales et alertes prêtes" : "Données locales disponibles sans réseau").font(.subheadline).foregroundStyle(.white.opacity(0.86))
                        Divider().overlay(.white.opacity(0.25))
                        Text(store.location.coordinate == nil ? "Aucun risque local sans position fiable" : (store.location.accuracy ?? 999) > 100 ? "Position trop imprécise pour calculer les distances" : nearbyRisks.isEmpty ? "Aucune donnée de risque connue dans un rayon de 10 km" : "\(nearbyRisks.count) signaux de démonstration dans un rayon de 10 km").font(.subheadline.bold()).foregroundStyle(.white).frame(maxWidth: .infinity, alignment: .leading)
                        ForEach(nearbyRisks.prefix(2)) { risk in HStack(spacing: 9) { Image(systemName: risk.category == "Taxi" ? "car.fill" : risk.category == "Change" ? "banknote.fill" : "fork.knife").font(.caption.bold()).foregroundStyle(.white).frame(width: 26, height: 26).background(TGColor.coral).clipShape(Circle()); VStack(alignment: .leading, spacing: 2) { Text(risk.category.uppercased()).font(.caption2.bold()).foregroundStyle(.white.opacity(0.72)); Text(risk.name).font(.caption.weight(.semibold)).foregroundStyle(.white) }; Spacer(); Text(risk.formattedDistance(from: store.location.coordinate)).font(.caption.bold()).foregroundStyle(.white.opacity(0.9)) } }
                    }.tgCard().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 22))
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

struct RiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 48.8584, longitude: 2.2945), span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035))
    @State private var selected: RiskPlace?
    @State private var showFullScreen = false
    @State private var hasInitiallyCentered = false

    private var displayedRisks: [RiskPlace] {
        guard let coordinate = store.location.coordinate, (store.location.accuracy ?? 999) <= 100 else { return [] }
        return trustedRisks.filter { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) <= 10000 }.sorted { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) < ($1.distance(from: coordinate) ?? .greatestFiniteMagnitude) }
    }

    private func recenter() {
        guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }
        withAnimation { region = MKCoordinateRegion(center: coordinate, span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035)) }
        hasInitiallyCentered = true
    }

    private func centerInitiallyIfNeeded() {
        guard !hasInitiallyCentered, store.location.coordinate != nil else { return }
        recenter()
    }

    private func zoom(by factor: Double) {
        let nextLatitude = min(max(region.span.latitudeDelta * factor, 0.001), 2.0)
        let nextLongitude = min(max(region.span.longitudeDelta * factor, 0.001), 2.0)
        withAnimation { region.span = MKCoordinateSpan(latitudeDelta: nextLatitude, longitudeDelta: nextLongitude) }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack { VStack(alignment: .leading) { Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Carte des risques").font(.title.bold()) }; Spacer(); Label(store.location.city, systemImage: "location.fill").font(.caption.bold()).padding(9).background(.white).clipShape(Capsule()) }.padding(.horizontal, 20).padding(.top, 10).padding(.bottom, 12)
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(9).background(.white).clipShape(Circle()).shadow(radius: 3) } } }.frame(height: 260).clipShape(RoundedRectangle(cornerRadius: 22)).padding(.horizontal, 20).overlay(alignment: .topLeading) { if !store.location.hasPermission || store.location.coordinate == nil || (store.location.accuracy ?? 999) > 100 { VStack(alignment: .leading, spacing: 7) { Label(store.location.locationStatus, systemImage: "location.slash").font(.caption.bold()); if let error = store.location.errorMessage { Text(error).font(.caption2).lineLimit(2) }; Button("Activer ma position") { store.location.requestPermission() }.font(.caption.bold()).buttonStyle(.borderedProminent).tint(TGColor.teal) }.padding(12).background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 14)).padding(10) } }.overlay(alignment: .bottomTrailing) { HStack(spacing: 8) { Button { recenter() } label: { Image(systemName: "location.fill").padding(10).background(.white).clipShape(Circle()) }; Button { showFullScreen = true } label: { Image(systemName: "arrow.up.left.and.arrow.down.right").padding(10).background(.white).clipShape(Circle()) } }.padding(12) }
                HStack(spacing: 8) { Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 34, height: 34) }; Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 34, height: 34) } }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(.leading, 30).padding(.top, -52)
                if store.location.coordinate == nil || (store.location.accuracy ?? 999) > 100 { Text(store.location.permissionDenied ? "Autorisez la localisation dans Réglages pour afficher les risques réellement proches de vous." : "La précision GPS est insuffisante pour afficher des distances fiables. Déplacez-vous à ciel ouvert puis réessayez.").font(.footnote).foregroundStyle(TGColor.muted).padding(.horizontal, 20).padding(.top, 14) }
                ScrollView { VStack(alignment: .leading, spacing: 10) { Text("Signaux à proximité").font(.title3.bold()).padding(.top, 16); if displayedRisks.isEmpty { Text("Aucune donnée géolocalisée autorisée n’est disponible dans un rayon de 10 km. Les sources officielles générales restent consultables dans Sécurité.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() }; ForEach(displayedRisks) { risk in Button { selected = risk } label: { HStack { VStack(spacing: 0) { Text("\(risk.confidenceScore)").font(.headline.bold()); Text("indicatif").font(.caption2) }.foregroundStyle(TGColor.coral).frame(width: 48, height: 48).background(TGColor.coral.opacity(0.1)).clipShape(Circle()); VStack(alignment: .leading) { Text(risk.name).font(.subheadline.bold()); Text("\(risk.category) · \(risk.formattedDistance(from: store.location.coordinate))").font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.summary).font(.caption).foregroundStyle(TGColor.muted).lineLimit(2) }; Spacer(); Image(systemName: "chevron.right").foregroundStyle(TGColor.muted) }.foregroundStyle(TGColor.ink).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } } }.padding(.horizontal, 20).padding(.bottom, 24) }
            }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { store.location.refresh(); centerInitiallyIfNeeded() }.onChange(of: store.location.lastUpdated) { _, _ in centerInitiallyIfNeeded() }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
            .fullScreenCover(isPresented: $showFullScreen) { FullScreenRiskMapView(region: $region, risks: displayedRisks, selected: $selected) }
        }
    }
}

struct FullScreenRiskMapView: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var region: MKCoordinateRegion
    let risks: [RiskPlace]
    @Binding var selected: RiskPlace?
    private func zoom(by factor: Double) { region.span = MKCoordinateSpan(latitudeDelta: min(max(region.span.latitudeDelta * factor, 0.001), 2.0), longitudeDelta: min(max(region.span.longitudeDelta * factor, 0.001), 2.0)) }
    var body: some View {
        NavigationStack {
            ZStack(alignment: .topTrailing) {
                Color.black.ignoresSafeArea()
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: risks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(10).background(.white).clipShape(Circle()).shadow(radius: 4) } } }.mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }.frame(maxWidth: .infinity, maxHeight: .infinity).background(Color.black).ignoresSafeArea().overlay(alignment: .bottomLeading) { HStack(spacing: 8) { Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 38, height: 38) }; Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 38, height: 38) } }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(.leading, 18).padding(.bottom, 28) }
            }.toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View { let risk: RiskPlace; var body: some View { ScrollView { VStack(alignment: .leading, spacing: 14) { Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.name).font(.title.bold()); Text("Indice indicatif : \(risk.confidenceScore)/100").font(.headline); Text(risk.summary).foregroundStyle(TGColor.muted); Label("\(risk.reportCount) signalements enregistrés", systemImage: "person.2.fill").font(.subheadline); Text(risk.source).font(.caption).foregroundStyle(TGColor.muted); Text(risk.freshnessLabel).font(.caption).foregroundStyle(TGColor.muted); ForEach(risk.signals, id: \.self) { signal in Text("• \(signal)") }; Spacer() }.padding(24) }.presentationDetents([.medium]) } }
''',
'ScannerView.swift': r'''import CoreImage
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
    var calculatedTotal: Double? {
        guard let subtotal else { return nil }
        return subtotal + (tax ?? 0) + (service ?? 0)
    }
    var difference: Double? {
        guard let total, let calculatedTotal else { return nil }
        return total - calculatedTotal
    }
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
                    if summary.hasData { VStack(alignment: .leading, spacing: 6) { Text("Lecture structurée").font(.subheadline.bold()); if let subtotal = summary.subtotal { Text("Sous-total : \(subtotal, specifier: \"%.2f\") \(summary.currency)") }; if let tax = summary.tax { Text("Taxes : \(tax, specifier: \"%.2f\") \(summary.currency)") }; if let service = summary.service { Text("Service : \(service, specifier: \"%.2f\") \(summary.currency)") }; if let total = summary.total { Text("Total détecté : \(total, specifier: \"%.2f\") \(summary.currency)").fontWeight(.bold) }; if let calculated = summary.calculatedTotal, let difference = summary.difference { Text(abs(difference) <= 0.05 ? "Total cohérent avec les lignes détectées : \(calculated, specifier: \"%.2f\") \(summary.currency)" : "Écart à vérifier : \(difference, specifier: \"%.2f\") \(summary.currency)").foregroundStyle(abs(difference) <= 0.05 ? .green : .red).font(.footnote.bold()) }; Text("Aucune référence officielle n’est disponible pour comparer automatiquement cette addition. Vérifiez toujours le document original.").font(.caption).foregroundStyle(TGColor.muted) }.padding(.top, 8) }
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
            let suspects = Set(lines.filter { line in
                let lower = line.lowercased()
                let feeTerms = ["service", "frais", "commission", "taxe", "tax", "tip", "gratuidad", "propina", "service charge", "surcharge", "supplement"]
                let exactFeeLabel = feeTerms.contains { lower.trimmingCharacters(in: .whitespacesAndNewlines).hasPrefix($0) }
                let hasAmount = line.range(of: #"\d+[.,]?\d*\s*(€|eur|usd|\\$|£|gbp|chf|%)?"#, options: .regularExpression) != nil
                return hasAmount && feeTerms.contains { lower.contains($0) } || exactFeeLabel && hasAmount
            })
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
''',
'SafetyView.swift': r'''import CoreLocation
import SwiftUI
import UIKit

struct SafetyView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var phraseIndex = 0
    @State private var alertsEnabled = UserDefaults.standard.object(forKey: "alertsEnabled") as? Bool ?? false
    private var emergencyNumber: String {
        let region = Locale.current.region?.identifier ?? ""
        if ["US", "CA"].contains(region) { return "911" }
        if region == "GB" { return "999" }
        if region == "AU" { return "000" }
        if region == "JP" { return "110" }
        return "112"
    }
    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 16) { HStack { VStack(alignment: .leading) { Text("PROTECTION ET RÉFÉRENCES").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Sécurité").font(.largeTitle.bold()) }; Spacer(); Label(store.location.hasPermission ? "Position protégée" : "Localisation requise", systemImage: store.location.hasPermission ? "checkmark.shield.fill" : "location.slash").font(.caption.bold()).foregroundStyle(store.location.hasPermission ? .green : TGColor.amber) }
            VStack(alignment: .leading, spacing: 12) { Label("BESOIN D’AIDE ?", systemImage: "shield.fill").font(.caption.weight(.heavy)).foregroundStyle(.white.opacity(0.85)); Text("Gardez vos phrases prêtes.").font(.title2.bold()).foregroundStyle(.white); Text("Affichez une phrase locale sans chercher dans vos réglages.").foregroundStyle(.white.opacity(0.85)); HStack { Button { phraseIndex = (phraseIndex + 1) % sampleSOS.count } label: { Label("Phrase locale", systemImage: "speaker.wave.2.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral); Button { if let url = URL(string: "tel://\(emergencyNumber)") { UIApplication.shared.open(url) } } label: { Label("Secours \(emergencyNumber)", systemImage: "phone.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral) } }.padding(18).frame(maxWidth: .infinity, alignment: .leading).background(TGColor.coral).clipShape(RoundedRectangle(cornerRadius: 22))
            VStack(alignment: .leading, spacing: 8) { HStack { Text(sampleSOS[phraseIndex].language).font(.caption.bold()).foregroundStyle(TGColor.teal); Spacer(); Text(store.network.isOnline ? "En ligne" : "Hors ligne").font(.caption.bold()).foregroundStyle(TGColor.muted) }; Text(sampleSOS[phraseIndex].local).font(.title3.bold()); Text(sampleSOS[phraseIndex].translation).foregroundStyle(TGColor.muted) }.tgCard()
            Text("Réglages de protection").font(.title3.bold()); Toggle("Alertes de proximité", isOn: $alertsEnabled).tint(TGColor.teal).disabled(trustedRisks.isEmpty).tgCard().onChange(of: alertsEnabled) { _, value in store.location.setProximityAlerts(value) }; Text(trustedRisks.isEmpty ? "Aucune source géolocalisée fiable · alertes indisponibles" : alertsEnabled ? (store.location.notificationPermission == .authorized ? "Alertes activées · régions iOS surveillées" : "Activation en attente de l’autorisation Notifications") : "Alertes désactivées").font(.caption.bold()).foregroundStyle(alertsEnabled ? TGColor.teal : TGColor.muted); Text("Les alertes utilisent la surveillance de régions iOS et nécessitent les autorisations de localisation et de notifications. Aucune alerte locale n’est activée sans une source géolocalisée autorisée. Les sources officielles générales sont consultables ci-dessous.").font(.caption).foregroundStyle(TGColor.muted); HStack { Image(systemName: store.network.isOnline ? "wifi" : "wifi.slash").foregroundStyle(store.network.isOnline ? .green : TGColor.amber); VStack(alignment: .leading) { Text("Mode hors ligne automatique").font(.subheadline.bold()); Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Connexion active · données locales prêtes" : "Aucune connexion · données locales utilisées").font(.caption).foregroundStyle(TGColor.muted) } }.tgCard()
            Text("Références de prix · \(store.location.city)").font(.title3.bold()); if prices(for: store.location.city).isEmpty { Text("Aucune référence officielle disponible pour cette ville. TravelGuard ne présente pas les données de démonstration comme des tarifs réels.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() } else { ForEach(prices(for: store.location.city)) { price in HStack { Text(price.label).bold(); Spacer(); Text(price.value) }.tgCard() } }; Text("Sources officielles").font(.title3.bold()); ForEach(officialSources) { source in Button { if let url = URL(string: source.url) { UIApplication.shared.open(url) } } label: { HStack { Image(systemName: "checkmark.seal").foregroundStyle(TGColor.teal); VStack(alignment: .leading) { Text(source.title).font(.subheadline.bold()); Text(source.scope).font(.caption).foregroundStyle(TGColor.muted) }; Spacer(); Image(systemName: "arrow.up.right").foregroundStyle(TGColor.muted) }.tgCard() } }
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { if trustedRisks.isEmpty { alertsEnabled = false } else if alertsEnabled { store.location.restoreProximityAlertsIfAuthorized() } } }
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
<key>NSCameraUsageDescription</key><string>TravelGuard utilise la caméra pour scanner les menus, additions et billets.</string>
<key>NSLocationWhenInUseUsageDescription</key><string>TravelGuard utilise votre position pour afficher les risques et tarifs autour de vous.</string>
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
(ROOT / 'README.md').write_text('''# TravelGuard Native iOS\n\nNative SwiftUI rebuild with no Expo, Metro, Node, or JavaScript runtime dependency. Open `TravelGuard.xcodeproj` on macOS with Xcode.\n\nFeatures: onboarding, location permission, dynamic city, local risk map, Vision OCR from camera/photo, fair-price references, automatic offline status, SOS phrases, and local persistence.\n''')
print(f'Generated {ROOT}')
