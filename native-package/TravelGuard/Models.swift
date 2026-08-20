import CoreLocation
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

private let localReferenceDate = Calendar.current.date(byAdding: .day, value: -2, to: Date()) ?? Date()

let sampleRisks = [
    RiskPlace(id: "taxi-1", name: "Taxi sans compteur", category: "Taxi", score: 31, summary: "Refus fréquent du compteur et tarif annoncé après la course.", latitude: 48.8584, longitude: 2.2945, signals: ["Pas de compteur visible", "Prix variable selon le client"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 12),
    RiskPlace(id: "exchange-1", name: "Change très défavorable", category: "Change", score: 44, summary: "Taux affiché sans frais réels clairement visibles.", latitude: 48.8606, longitude: 2.3376, signals: ["Commission peu lisible", "Écart au taux de référence"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 8),
    RiskPlace(id: "restaurant-1", name: "Menu touristique", category: "Restaurant", score: 58, summary: "Suppléments signalés sur les terrasses et accompagnements.", latitude: 48.8530, longitude: 2.3499, signals: ["Menu sans prix détaillés", "Service ajouté automatiquement"], source: "Donnée locale de démonstration", updatedAt: localReferenceDate, reportCount: 5)
]

let samplePrices = [
    FairPrice(id: "coffee", label: "Café", value: "2,50 €", reference: "Repère local indicatif", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate),
    FairPrice(id: "taxi", label: "Course taxi", value: "12–18 €", reference: "Trajet urbain standard", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate),
    FairPrice(id: "museum", label: "Billet attraction", value: "18 €", reference: "Tarif officiel indicatif", city: "Paris", source: "Référence locale de démonstration", updatedAt: localReferenceDate)
]

let sampleSOS = [
    SOSPhrase(language: "Français", local: "Je veux le prix officiel, s’il vous plaît.", translation: "Phrase de contrôle du tarif"),
    SOSPhrase(language: "Anglais", local: "Please use the official meter.", translation: "Merci d’utiliser le compteur officiel."),
    SOSPhrase(language: "Espagnol", local: "Quiero el precio oficial, por favor.", translation: "Je veux le prix officiel, s’il vous plaît."),
    SOSPhrase(language: "Italien", local: "Vorrei il prezzo ufficiale, per favore.", translation: "Je voudrais le prix officiel, s’il vous plaît.")
]
