import SwiftUI

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
