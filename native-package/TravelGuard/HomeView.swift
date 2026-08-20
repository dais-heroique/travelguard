import Foundation
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
