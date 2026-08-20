import Foundation
import MapKit
import SwiftUI

struct RiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 48.8584, longitude: 2.2945), span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035))
    @State private var selected: RiskPlace?
    @State private var showFullScreen = false
    @State private var hasInitiallyCentered = false

    private var displayedRisks: [RiskPlace] {
        guard let coordinate = store.location.coordinate, (store.location.accuracy ?? 999) <= 100 else { return [] }
        return sampleRisks.filter { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) <= 10000 }.sorted { ($0.distance(from: coordinate) ?? .greatestFiniteMagnitude) < ($1.distance(from: coordinate) ?? .greatestFiniteMagnitude) }
    }

    private func recenter() {
        guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }
        withAnimation { region = MKCoordinateRegion(center: coordinate, span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035)) }
        hasInitiallyCentered = true
    }

    private func centerInitiallyIfNeeded() {
        guard !hasInitiallyCentered, store.location.coordinate != nil else { return }
        recenter()
    }

    private func zoom(by factor: Double) {
        let nextLatitude = min(max(region.span.latitudeDelta * factor, 0.001), 2.0)
        let nextLongitude = min(max(region.span.longitudeDelta * factor, 0.001), 2.0)
        withAnimation { region.span = MKCoordinateSpan(latitudeDelta: nextLatitude, longitudeDelta: nextLongitude) }
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack { VStack(alignment: .leading) { Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Carte des risques").font(.title.bold()) }; Spacer(); Label(store.location.city, systemImage: "location.fill").font(.caption.bold()).padding(9).background(.white).clipShape(Capsule()) }.padding(.horizontal, 20).padding(.top, 10).padding(.bottom, 12)
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(9).background(.white).clipShape(Circle()).shadow(radius: 3) } } }.frame(height: 260).clipShape(RoundedRectangle(cornerRadius: 22)).padding(.horizontal, 20).overlay(alignment: .topLeading) { if !store.location.hasPermission || store.location.coordinate == nil || (store.location.accuracy ?? 999) > 100 { VStack(alignment: .leading, spacing: 7) { Label(store.location.locationStatus, systemImage: "location.slash").font(.caption.bold()); if let error = store.location.errorMessage { Text(error).font(.caption2).lineLimit(2) }; Button("Activer ma position") { store.location.requestPermission() }.font(.caption.bold()).buttonStyle(.borderedProminent).tint(TGColor.teal) }.padding(12).background(.thinMaterial).clipShape(RoundedRectangle(cornerRadius: 14)).padding(10) } }.overlay(alignment: .bottomTrailing) { HStack(spacing: 8) { Button { recenter() } label: { Image(systemName: "location.fill").padding(10).background(.white).clipShape(Circle()) }; Button { showFullScreen = true } label: { Image(systemName: "arrow.up.left.and.arrow.down.right").padding(10).background(.white).clipShape(Circle()) } }.padding(12) }
                HStack(spacing: 8) { Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 34, height: 34) }; Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 34, height: 34) } }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(.leading, 30).padding(.top, -52)
                if store.location.coordinate == nil || (store.location.accuracy ?? 999) > 100 { Text(store.location.permissionDenied ? "Autorisez la localisation dans Réglages pour afficher les risques réellement proches de vous." : "La précision GPS est insuffisante pour afficher des distances fiables. Déplacez-vous à ciel ouvert puis réessayez.").font(.footnote).foregroundStyle(TGColor.muted).padding(.horizontal, 20).padding(.top, 14) }
                ScrollView { VStack(alignment: .leading, spacing: 10) { Text("Signaux à proximité").font(.title3.bold()).padding(.top, 16); if displayedRisks.isEmpty { Text("Aucune donnée de risque connue dans un rayon de 10 km. Les données embarquées sont une démonstration et ne constituent pas une base locale vérifiée.").font(.subheadline).foregroundStyle(TGColor.muted).tgCard() }; ForEach(displayedRisks) { risk in Button { selected = risk } label: { HStack { VStack(spacing: 0) { Text("\(risk.confidenceScore)").font(.headline.bold()); Text("indicatif").font(.caption2) }.foregroundStyle(TGColor.coral).frame(width: 48, height: 48).background(TGColor.coral.opacity(0.1)).clipShape(Circle()); VStack(alignment: .leading) { Text(risk.name).font(.subheadline.bold()); Text("\(risk.category) · \(risk.formattedDistance(from: store.location.coordinate))").font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.summary).font(.caption).foregroundStyle(TGColor.muted).lineLimit(2) }; Spacer(); Image(systemName: "chevron.right").foregroundStyle(TGColor.muted) }.foregroundStyle(TGColor.ink).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } } }.padding(.horizontal, 20).padding(.bottom, 24) }
            }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { store.location.refresh(); centerInitiallyIfNeeded() }.onChange(of: store.location.lastUpdated) { _, _ in centerInitiallyIfNeeded() }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
            .fullScreenCover(isPresented: $showFullScreen) { FullScreenRiskMapView(region: $region, risks: displayedRisks, selected: $selected) }
        }
    }
}

struct FullScreenRiskMapView: View {
    @Environment(\.dismiss) private var dismiss
    @Binding var region: MKCoordinateRegion
    let risks: [RiskPlace]
    @Binding var selected: RiskPlace?
    private func zoom(by factor: Double) { region.span = MKCoordinateSpan(latitudeDelta: min(max(region.span.latitudeDelta * factor, 0.001), 2.0), longitudeDelta: min(max(region.span.longitudeDelta * factor, 0.001), 2.0)) }
    var body: some View {
        NavigationStack {
            ZStack(alignment: .topTrailing) {
                Color.black.ignoresSafeArea()
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: risks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(10).background(.white).clipShape(Circle()).shadow(radius: 4) } } }.mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }.frame(maxWidth: .infinity, maxHeight: .infinity).background(Color.black).ignoresSafeArea().overlay(alignment: .bottomLeading) { HStack(spacing: 8) { Button { zoom(by: 0.55) } label: { Image(systemName: "plus").frame(width: 38, height: 38) }; Button { zoom(by: 1.8) } label: { Image(systemName: "minus").frame(width: 38, height: 38) } }.font(.headline).foregroundStyle(TGColor.ink).background(.ultraThinMaterial).clipShape(Capsule()).padding(.leading, 18).padding(.bottom, 28) }
            }.toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View { let risk: RiskPlace; var body: some View { ScrollView { VStack(alignment: .leading, spacing: 14) { Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.name).font(.title.bold()); Text("Indice indicatif : \(risk.confidenceScore)/100").font(.headline); Text(risk.summary).foregroundStyle(TGColor.muted); Label("\(risk.reportCount) signalements enregistrés", systemImage: "person.2.fill").font(.subheadline); Text(risk.source).font(.caption).foregroundStyle(TGColor.muted); Text(risk.freshnessLabel).font(.caption).foregroundStyle(TGColor.muted); ForEach(risk.signals, id: \.self) { signal in Text("• \(signal)") }; Spacer() }.padding(24) }.presentationDetents([.medium]) } }
