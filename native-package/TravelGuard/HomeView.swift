import SwiftUI

struct HomeView: View {
    @EnvironmentObject private var store: TravelGuardStore
    var place: String { store.location.country.isEmpty ? store.location.city : "\(store.location.city) · \(store.location.country)" }
    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: 18) {
                    HStack { VStack(alignment: .leading, spacing: 4) { Text("TRAVELGUARD").font(.caption.weight(.heavy)).tracking(1.5).foregroundStyle(TGColor.muted); Text("Voyagez l’esprit léger.").font(.system(size: 29, weight: .bold, design: .rounded)).foregroundStyle(TGColor.ink) }; Spacer(); Text("TG").font(.headline).foregroundStyle(.white).frame(width: 42, height: 42).background(TGColor.teal).clipShape(Circle()) }
                    VStack(alignment: .leading, spacing: 12) { Label("PROTECTION ACTIVE", systemImage: "checkmark.shield.fill").font(.caption.weight(.heavy)).foregroundStyle(TGColor.mint); Text(place).font(.title2.bold()).foregroundStyle(.white); Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Connexion active · données locales prêtes" : "Hors ligne · données locales utilisées").font(.subheadline).foregroundStyle(.white.opacity(0.86)) }.tgCard().background(TGColor.teal).clipShape(RoundedRectangle(cornerRadius: 22))
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
    let title: String; let icon: String; let tab: Int
    var body: some View { Button {} label: { VStack(alignment: .leading, spacing: 10) { Image(systemName: icon).font(.title3).foregroundStyle(TGColor.teal); Text(title).font(.subheadline.weight(.bold)).foregroundStyle(TGColor.ink) }.frame(maxWidth: .infinity, minHeight: 82, alignment: .leading).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } }
}
