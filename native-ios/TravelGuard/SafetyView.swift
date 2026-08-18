import CoreLocation
import SwiftUI
import UIKit

struct SafetyView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var phraseIndex = 0
    @State private var alertsEnabled = UserDefaults.standard.object(forKey: "alertsEnabled") as? Bool ?? true
    var body: some View {
        NavigationStack { ScrollView { VStack(alignment: .leading, spacing: 16) { HStack { VStack(alignment: .leading) { Text("PROTECTION ET RÉFÉRENCES").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Sécurité").font(.largeTitle.bold()) }; Spacer(); Label("Active", systemImage: "checkmark.shield.fill").font(.caption.bold()).foregroundStyle(.green) }
            VStack(alignment: .leading, spacing: 12) { Label("BESOIN D’AIDE ?", systemImage: "shield.fill").font(.caption.weight(.heavy)).foregroundStyle(.white.opacity(0.85)); Text("Gardez vos phrases prêtes.").font(.title2.bold()).foregroundStyle(.white); Text("Affichez une phrase locale sans chercher dans vos réglages.").foregroundStyle(.white.opacity(0.85)); HStack { Button { phraseIndex = (phraseIndex + 1) % sampleSOS.count } label: { Label("Phrase locale", systemImage: "speaker.wave.2.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral); Button { if let url = URL(string: "tel://112") { UIApplication.shared.open(url) } } label: { Label("Secours", systemImage: "phone.fill") }.buttonStyle(.borderedProminent).tint(.white).foregroundStyle(TGColor.coral) } }.padding(18).frame(maxWidth: .infinity, alignment: .leading).background(TGColor.coral).clipShape(RoundedRectangle(cornerRadius: 22))
            VStack(alignment: .leading, spacing: 8) { HStack { Text(sampleSOS[phraseIndex].language).font(.caption.bold()).foregroundStyle(TGColor.teal); Spacer(); Text("Hors ligne").font(.caption.bold()).foregroundStyle(TGColor.muted) }; Text(sampleSOS[phraseIndex].local).font(.title3.bold()); Text(sampleSOS[phraseIndex].translation).foregroundStyle(TGColor.muted) }.tgCard()
            Text("Réglages de protection").font(.title3.bold()); Toggle("Alertes de proximité", isOn: $alertsEnabled).tint(TGColor.teal).tgCard().onChange(of: alertsEnabled) { _, value in UserDefaults.standard.set(value, forKey: "alertsEnabled") }; HStack { Image(systemName: store.network.isOnline ? "wifi" : "wifi.slash").foregroundStyle(store.network.isOnline ? .green : TGColor.amber); VStack(alignment: .leading) { Text("Mode hors ligne automatique").font(.subheadline.bold()); Text(store.network.isChecking ? "Vérification de la connexion…" : store.network.isOnline ? "Connexion active · données locales prêtes" : "Aucune connexion · données locales utilisées").font(.caption).foregroundStyle(TGColor.muted) } }.tgCard()
            Text("Indice du juste prix · \(store.location.city)").font(.title3.bold()); ForEach(samplePrices) { price in HStack { Text(price.label).bold(); Spacer(); Text(price.value) }.tgCard() }
        }.padding(20).padding(.bottom, 30) }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true) }
    }
}
