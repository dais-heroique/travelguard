import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var store: TravelGuardStore
    var place: String { store.location.country.isEmpty ? store.location.city : "\(store.location.city) · \(store.location.country)" }
    private var nearbyRisks: [RiskPlace] {
        guard let coordinate = store.location.coordinate else { return sampleRisks }
        return sampleRisks.enumerated().map { index, risk in
            let offsets = [(0.002, 0.002), (-0.002, 0.001), (0.001, -0.002)]; let offset = offsets[index % offsets.count]
            return RiskPlace(id: risk.id, name: risk.name, category: risk.category, score: risk.score, summary: risk.summary, latitude: coordinate.latitude + offset.0, longitude: coordinate.longitude + offset.1, signals: risk.signals)
        }
    }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack { VStack(alignment: .leading, spacing: 4) { Text("TRAVELGUARD").font(.caption.weight(.heavy)).tracking(1.5).foregroundStyle(TGColor.muted); Text("Voyagez l’esprit léger.").font(.system(size: 29, weight: .bold, design: .rounded)).foregroundStyle(TGColor.ink) }; Spacer(); Text("TG").font(.headline).foregroundStyle(.white).frame(width: 42, height: 42).background(TGColor.teal).clipShape(Circle()) }
                    VStack(alignment: .leading, spacing: 12) {
                        Label("PROTECTION ACTIVE", systemImage: "checkmark.shield.fill").font(.caption.weight(.heavy)).foregroundStyle(TGColor.mint)
                        Text(place).font(.title2.bold()).foregroundStyle(.white)
                        HStack(spacing: 14) { Label(store.location.coordinate == nil ? "Position à activer" : "Position détectée", systemImage: "location.fill"); Label(store.network.isOnline ? "En ligne" : "Hors ligne", systemImage: store.network.isOnline ? "wifi" : "wifi.slash") }.font(.caption.weight(.semibold)).foregroundStyle(.white.opacity(0.88))
                        Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Données locales et alertes prêtes" : "Données locales disponibles sans réseau").font(.subheadline).foregroundStyle(.white.opacity(0.86))
                        Divider().overlay(.white.opacity(0.25))
                        Text("\(nearbyRisks.count) risques surveillés près de vous").font(.subheadline.bold()).foregroundStyle(.white)
                        ForEach(nearbyRisks.prefix(2)) { risk in HStack(spacing: 8) { Circle().fill(Color.red).frame(width: 8, height: 8); Text(risk.name).font(.caption.weight(.semibold)).foregroundStyle(.white); Spacer(); Text("\(risk.score)/100").font(.caption.bold()).foregroundStyle(.white.opacity(0.9)) } }
                    }.tgCard().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 22))
                    Text("Besoin d’un contrôle rapide ?").font(.title3.bold()).foregroundStyle(TGColor.ink)
                    HStack(spacing: 10) { QuickLink(title: "Voir la carte", icon: "map.fill", tab: 1); QuickLink(title: "Scanner", icon: "viewfinder", tab: 2); QuickLink(title: "Juste prix", icon: "checkmark.seal.fill", tab: 3) }
                    Text("Juste prix près de vous").font(.title3.bold()).foregroundStyle(TGColor.ink)
                    ForEach(samplePrices) { price in HStack { Image(systemName: "checkmark.seal.fill").foregroundStyle(.green); VStack(alignment: .leading) { Text(price.label).font(.subheadline.bold()); Text(price.reference).font(.caption).foregroundStyle(TGColor.muted) }; Spacer(); Text(price.value).bold() }.tgCard() }
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
