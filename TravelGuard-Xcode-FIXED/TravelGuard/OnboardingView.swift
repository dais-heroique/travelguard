import SwiftUI

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
