import SwiftUI

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
    var body: some View {
        TabView {
            HomeView().tabItem { Label("Accueil", systemImage: "house.fill") }
            RiskMapView().tabItem { Label("Carte", systemImage: "map.fill") }
            ScannerView().tabItem { Label("Scanner", systemImage: "viewfinder") }
            SafetyView().tabItem { Label("Sécurité", systemImage: "shield.fill") }
        }
    }
}
