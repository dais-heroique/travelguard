import Foundation
import MapKit
import SwiftUI
import UIKit

struct RiskMapLegend: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 5) {
            Label("Faible", systemImage: "circle.fill").foregroundStyle(.green)
            Label("Modéré", systemImage: "circle.fill").foregroundStyle(.orange)
            Label("Élevé", systemImage: "circle.fill").foregroundStyle(.red)
            Label("Zone", systemImage: "circle.dotted").foregroundStyle(.red)
        }
        .font(.caption2.bold())
        .padding(9)
        .background(.thinMaterial)
        .clipShape(RoundedRectangle(cornerRadius: 12))
    }
}

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
    @State private var positionTask: Task<Void, Never>?
    @State private var viewportTask: Task<Void, Never>?

    private var displayedRisks: [RiskPlace] { RiskPlace.inViewport(region, risks: store.risks) }

    private func requestViewportRisks() {
        viewportTask?.cancel()
        let snapshot = region
        guard snapshot.span.latitudeDelta <= 90, snapshot.span.longitudeDelta <= 180 else { return }
        viewportTask = Task { @MainActor in
            try? await Task.sleep(nanoseconds: 400_000_000)
            guard !Task.isCancelled else { return }
            let lat = min(max(snapshot.span.latitudeDelta, 0.001), 90)
            let lon = min(max(snapshot.span.longitudeDelta, 0.001), 180)
            let west = ((snapshot.center.longitude - lon / 2 + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
            let east = ((snapshot.center.longitude + lon / 2 + 180).truncatingRemainder(dividingBy: 360) + 360).truncatingRemainder(dividingBy: 360) - 180
            let south = max(-90, snapshot.center.latitude - lat / 2)
            let north = min(90, snapshot.center.latitude + lat / 2)
            await store.synchronizeRisks(in: RiskBoundingBox(west: west, south: south, east: east, north: north, page: 1))
        }
    }

    private func recenter() {
        positionTask?.cancel()
        positionTask = nil
        guard let coordinate = store.location.coordinate else {
            store.location.requestPermission()
            return
        }
        suppressNextCameraChange = true
        withAnimation {
            region = MKCoordinateRegion(center: coordinate, span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035))
        }
        hasInitiallyCentered = true
        isRequestingPosition = false
    }

    private func centerInitiallyIfNeeded() {
        guard !hasInitiallyCentered, !hasUserInteractedWithMap, store.location.coordinate != nil else { return }
        recenter()
    }

    private func zoom(by factor: Double) {
        suppressNextCameraChange = true
        hasUserInteractedWithMap = true
        let latitude = min(max(region.span.latitudeDelta * factor, 0.001), 180.0)
        let longitude = min(max(region.span.longitudeDelta * factor, 0.001), 360.0)
        withAnimation { region.span = MKCoordinateSpan(latitudeDelta: latitude, longitudeDelta: longitude) }
    }

    @ViewBuilder private func annotation(for risk: RiskPlace) -> some View {
        Button { selected = risk } label: {
            Image(systemName: risk.locationPrecision == .point ? "exclamationmark.triangle.fill" : "circle.dotted")
                .foregroundStyle(risk.score >= 60 ? .red : risk.score >= 30 ? .orange : .green)
                .padding(9)
                .background(.white)
                .clipShape(Circle())
                .shadow(radius: 3)
        }
        .accessibilityLabel("\(risk.name), risque \(risk.severityLabel), confiance \(risk.confidenceScore) pour cent")
    }

    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack {
                    VStack(alignment: .leading) {
                        Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted)
                        Text("Carte des risques").font(.title.bold())
                    }
                    Spacer()
                    Text(store.location.city.isEmpty ? "Localisation…" : store.location.city)
                        .font(.caption.bold())
                        .padding(9)
                        .background(.white)
                        .clipShape(Capsule())
                }
                .padding(.horizontal, 20)
                .padding(.top, 10)
                .padding(.bottom, 12)

                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in
                    MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) {
                        annotation(for: risk)
                    }
                }
                .onMapCameraChange(frequency: .onEnd) { _ in
                    if suppressNextCameraChange {
                        suppressNextCameraChange = false
                    } else {
                        hasUserInteractedWithMap = true
                        hasInitiallyCentered = true
                        requestViewportRisks()
                    }
                }
                .frame(height: min(max(UIScreen.main.bounds.height * 0.52, 420), 620))
                .overlay(alignment: .topLeading) { RiskMapLegend().padding(10) }
                .clipShape(RoundedRectangle(cornerRadius: 22))
                .padding(.horizontal, 20)

                if displayedRisks.isEmpty {
                    Text(store.risks.isEmpty ? "Aucun risque synchronisé dans l’application." : "Aucun risque connu dans la zone visible.")
                        .font(.subheadline)
                        .foregroundStyle(TGColor.muted)
                        .tgCard()
                        .padding(20)
                } else {
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 10) {
                            Text("Signaux dans la zone visible").font(.title3.bold())
                            ForEach(displayedRisks) { risk in
                                Button { selected = risk } label: {
                                    HStack {
                                        Text(risk.severityLabel.capitalized)
                                            .font(.caption.bold())
                                            .foregroundStyle(TGColor.coral)
                                        VStack(alignment: .leading) {
                                            Text(risk.name).font(.subheadline.bold())
                                            Text(risk.category).font(.caption).foregroundStyle(TGColor.teal)
                                            Text(risk.summary).font(.caption).foregroundStyle(TGColor.muted).lineLimit(2)
                                        }
                                        Spacer()
                                        Image(systemName: "chevron.right").foregroundStyle(TGColor.muted)
                                    }
                                    .foregroundStyle(TGColor.ink)
                                    .padding(12)
                                    .background(.white)
                                    .clipShape(RoundedRectangle(cornerRadius: 16))
                                }
                            }
                        }
                        .padding(20)
                    }
                }
            }
            .background(TGColor.ivory)
            .navigationTitle("")
            .toolbar(.hidden, for: .navigationBar)
            .navigationBarHidden(true)
            .onAppear { store.location.refresh(); centerInitiallyIfNeeded() }
            .onChange(of: store.location.lastUpdated) { _, _ in centerInitiallyIfNeeded() }
            .onDisappear { positionTask?.cancel(); viewportTask?.cancel() }
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
    private func recenter() { if store.location.isUsingCachedLocation { store.location.refresh(); return }; guard let coordinate = store.location.coordinate else { store.location.requestPermission(); return }; region.center = coordinate }
    private func zoom(by factor: Double) { region.span = MKCoordinateSpan(latitudeDelta: min(max(region.span.latitudeDelta * factor, 0.001), 180), longitudeDelta: min(max(region.span.longitudeDelta * factor, 0.001), 360)) }
    var body: some View {
        NavigationStack {
            Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in
                MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) {
                    Button { selected = risk } label: { Image(systemName: "circle.fill").frame(width: 44, height: 44).foregroundStyle(.red).padding(10).background(.white).clipShape(Circle()) }
                }
            }
            .mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }
            .toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View {
    let risk: RiskPlace
    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 14) {
                Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal)
                Text(risk.name).font(.title.bold())
                Text("Risque : \(risk.severityLabel.capitalized)").font(.headline)
                Text(risk.reliabilityLabel).foregroundStyle(TGColor.teal)
                Text(risk.summary).foregroundStyle(TGColor.muted)
                Text("Précision géographique : \(risk.locationPrecision == .point ? "point" : risk.locationPrecision == .neighborhood ? "quartier" : risk.locationPrecision == .city ? "ville" : "pays")").font(.caption).foregroundStyle(TGColor.muted)
                Text(risk.source).font(.caption).foregroundStyle(TGColor.muted)
                Text(risk.freshnessLabel).font(.caption).foregroundStyle(TGColor.muted)
                ForEach(risk.signals, id: \.self) { Text("• \($0)") }
            }
            .padding(24)
        }
        .presentationDetents([.medium])
    }
}
