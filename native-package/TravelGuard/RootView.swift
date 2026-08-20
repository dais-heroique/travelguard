import SwiftUI

struct RootView: View {
    @EnvironmentObject private var store: TravelGuardStore

    var body: some View {
        Group {
            if store.onboardingComplete { MainTabView() } else { OnboardingView() }
        }
        .tint(TGColor.teal)
        .background(TGColor.ivory.ignoresSafeArea())
        .task { await store.synchronizeRisks() }
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
