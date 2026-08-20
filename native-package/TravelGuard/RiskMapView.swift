import Foundation
import MapKit
import SwiftUI

struct RiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 0, longitude: 0), span: MKCoordinateSpan(latitudeDelta: 45, longitudeDelta: 45))
    @State private var selected: RiskPlace?
    @State private var showFullScreen = false
    @State private var hasInitiallyCentered = false
    @State private var hasUserInteractedWithMap = false
    @State private var suppressNextCameraChange = false
    @State private var isRequestingPosition = false
    @State private var positionSearchTimedOut = false

    private var displayedRisks: [RiskPlace] { RiskPlace.inViewport(region, risks: store.risks) }

    private func recenter() {
        if store.location.isUsingCachedLocation { isRequestingPosition = true; positionSearchTimedOut = false; store.location.refresh(); Task { try? await Task.sleep(for: .seconds(15)); if isRequestingPosition { positionSearchTimedOut = true; isRequestingPosition = false } }; return
        guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }
        suppressNextCameraChange = true
        withAnimation { region = MKCoordinateRegion(center: coordinate, span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035)) }
        hasInitiallyCentered = true
    }

    private func centerInitiallyIfNeeded() {
        guard !hasInitiallyCentered, !hasUserInteractedWithMap, store.location.coordinate != nil else { return }
        recenter()
    }

    private func zoom(by factor: Double) {
        suppressNextCameraChange = true
        hasUserInteractedWithMap = true
        let nextLatitude = min(max(region.span.latitudeDelta * factor, 0.001), 0.35)
        let nextLongitude = min(max(region.span.longitudeDelta * factor, 0.001), 0.35)
        withAnimation { region.span = MKCoordinateSpan(latitudeDelta: nextLatitude, longitudeDelta: nextLongitude) }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack { VStack(alignment: .leading) { Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Carte des risques").font(.title.bold()) }; Spacer(); Label((store.location.city.isEmpty || store.location.city == "Localisation requise" || store.location.city == "Position indisponible") ? "Localisation…" : store.location.city, systemImage: "location.fill").font(.caption.bold()).padding(9).background(.white).clipShape(Capsule()) }.padding(.horizontal, 20).padding(.top, 10).padding(.bottom, 12)
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(risk.score >= 80 ? .purple : risk.score >= 60 ? .red : risk.score >= 30 ? .orange : .green).padding(9).background(.white).clipShape(Circle()).shadow(radius: 3) }.accessibilityLabel("\(risk.name), risque \(risk.severityLabel), confiance \(risk.confidenceScore) pour cent") } }.onMapCameraChange(frequency: .onEnd) { _ in if suppressNextCameraChange { suppressNextCameraChange = false } else { hasUserInteractedWithMap = true; hasInitiallyCentered = true } }.frame(height: 260).clipShape(RoundedRectangle(cornerRadius: 22)).padding(.horizontal, 20).overlay(alignment: .topLeading) { if !store.location.hasPermission || store.location.coordinate == nil || (store.location.accuracy ?? 999) > 200 { VStack(alignment: .leading, spacing: 7) { Label(store.location.locationStatus, systemImage: "location.slash").font(.caption.bold()); if let error = store.location.errorMessage { Text(error).font(.caption2).lineLimit(2) }; if let geoError = store.location.geocodingErrorMessage { Text(geoError).font(.caption2).lineLimit(2) }; Button(!store.location.servicesEnabled ? "Ouvrir Réglages" : store.location.permissionDenied || !store.location.hasPermission ? "Activer ma position" : "Améliorer la précision") { store.location.requestPermission() }.font(.caption.bold()).buttonStyle(.borderedProminent).tint(TGColor.teal) }.padding(12).background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 14)).padding(10) } }.overlay(alignment: .bottomTrailing) { HStack(spacing: 8) { Button { recenter() } label: { positionSearchTimedOut ? AnyView(Image(systemName: "arrow.clockwise").frame(width: 44, height: 44)) : isRequestingPosition ? AnyView(ProgressView().frame(width: 44, height: 44)) : AnyView(Image(systemName: "location.fill").frame(width: 44, height: 44)) }.background(.white).clipShape(Circle()).accessibilityLabel(positionSearchTimedOut ? "Position précise indisponible · Réessayer" : isRequestingPosition ? "Recherche de votre position" : "Recentrer sur ma position"); Button { showFullScreen = true } label: { Image(systemName: "arrow.up.left.and.arrow.down.right").padding(10).background(.white).clipShape(Circle()) } }.padding(12) }.overlay(alignment: .bottomLeading) { HStack(spacing: 8) { Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 44, height: 44) }.accessibilityLabel("Zoomer"); Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 44, height: 44) }.accessibilityLabel("Dézoomer") }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(12) }
                if store.location.coordinate == nil || (store.location.accuracy ?? 999) > 200 { Text(store.location.permissionDenied ? "Autorisez la localisation dans Réglages pour afficher les risques réellement proches de vous." : store.location.coordinate == nil ? "Localisation en cours… Activez votre position pour afficher la carte autour de vous." : "Position très imprécise : les distances sont masquées.").font(.footnote).foregroundStyle(TGColor.muted).padding(.horizontal, 20).padding(.top, 14) }
                ScrollView { VStack(alignment: .leading, spacing: 10) { Text("Signaux dans la zone visible").font(.title3.bold()).padding(.top, 16); if displayedRisks.isEmpty { Text(store.location.coordinate == nil ? "Localisation en cours…" : (store.location.accuracy ?? 999) > 200 ? "Position très imprécise…" : store.risks.isEmpty ? "Aucun risque synchronisé dans l’application." : store.riskDataIsStale ? "Aucun risque connu dans les données disponibles. \(store.riskDataFreshnessLabel). Déplacez la carte pour explorer." : "Aucun risque connu dans la zone visible. \(store.risks.count) risques sont disponibles dans la base. Déplacez ou zoomez la carte pour explorer.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() }; ForEach(displayedRisks) { risk in Button { selected = risk } label: { HStack { VStack(spacing: 0) { Text(risk.severityLabel.capitalized).font(.caption.bold()); Text("Risque").font(.caption2) }.accessibilityElement(children: .combine).foregroundStyle(TGColor.coral).frame(width: 48, height: 48).background(TGColor.coral.opacity(0.1)).clipShape(Circle()); VStack(alignment: .leading) { Text(risk.name).font(.subheadline.bold()); Text("\(risk.category) · \(((store.location.accuracy ?? 999) > 200 ? "Distance indisponible" : risk.formattedDistance(from: store.location.coordinate)))").font(.caption.bold()).foregroundStyle(TGColor.teal); if let accuracy = store.location.accuracy, accuracy > 50 { Text(accuracy > 200 ? "Distance indisponible · position très imprécise" : "Distance approximative · GPS ±\(Int(accuracy)) m").font(.caption2).foregroundStyle(TGColor.amber) }; Text(risk.summary).font(.caption).foregroundStyle(TGColor.muted).lineLimit(2) }; Spacer(); Image(systemName: "chevron.right").foregroundStyle(TGColor.muted) }.foregroundStyle(TGColor.ink).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } } }.padding(.horizontal, 20).padding(.bottom, 24) }
            }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { store.location.refresh(); centerInitiallyIfNeeded() }.onChange(of: store.location.lastUpdated) { _, _ in isRequestingPosition = false; positionSearchTimedOut = false; centerInitiallyIfNeeded() }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
            .fullScreenCover(isPresented: $showFullScreen) { FullScreenRiskMapView(region: $region, selected: $selected) }
        }
    }
}

struct FullScreenRiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @Environment(\.dismiss) private var dismiss
    @Binding var region: MKCoordinateRegion
    @Binding var selected: RiskPlace?
    private var displayedRisks: [RiskPlace] { RiskPlace.inViewport(region, risks: store.risks) }
    private func recenter() { if store.location.isUsingCachedLocation { store.location.refresh(); return }; guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }; region.center = coordinate; region.span = MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035) }
    private func zoom(by factor: Double) { region.span = MKCoordinateSpan(latitudeDelta: min(max(region.span.latitudeDelta * factor, 0.001), 0.35), longitudeDelta: min(max(region.span.longitudeDelta * factor, 0.001), 0.35)) }
    var body: some View {
        NavigationStack {
            ZStack(alignment: .topTrailing) {
                Color.black.ignoresSafeArea()
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(risk.score >= 80 ? .purple : risk.score >= 60 ? .red : risk.score >= 30 ? .orange : .green).padding(10).background(.white).clipShape(Circle()).shadow(radius: 4) }.accessibilityLabel("\(risk.name), risque \(risk.severityLabel), confiance \(risk.confidenceScore) pour cent") } }.mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }.frame(maxWidth: .infinity, maxHeight: .infinity).background(Color.black).ignoresSafeArea().overlay(alignment: .bottomLeading) { HStack(spacing: 8) { Button { recenter() } label: { Image(systemName: "location.fill").frame(width: 44, height: 44) }.accessibilityLabel("Recentrer sur ma position"); Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 44, height: 44) }.accessibilityLabel("Zoomer"); Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 44, height: 44) }.accessibilityLabel("Dézoomer") }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(.leading, 18).padding(.bottom, 28) }
            }.toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View { let risk: RiskPlace; var body: some View { ScrollView { VStack(alignment: .leading, spacing: 14) { Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.name).font(.title.bold()); VStack(alignment: .leading, spacing: 4) { Text("Risque : \(risk.severityLabel.capitalized)").font(.headline); Text("Confiance : \(risk.confidenceScore)%").font(.subheadline).foregroundStyle(TGColor.teal) }; Text(risk.summary).foregroundStyle(TGColor.muted); Label("\(risk.reportCount) signalements enregistrés", systemImage: "person.2.fill").font(.subheadline); Text(risk.source).font(.caption).foregroundStyle(TGColor.muted); Text(risk.freshnessLabel).font(.caption).foregroundStyle(TGColor.muted); ForEach(risk.signals, id: \.self) { signal in Text("• \(signal)") }; Spacer() }.padding(24) }.presentationDetents([.medium]) } }
