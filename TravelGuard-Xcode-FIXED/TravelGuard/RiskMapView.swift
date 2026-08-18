import MapKit
import SwiftUI

struct RiskMapView: View {
    @EnvironmentObject private var store: TravelGuardStore
    @State private var region = MKCoordinateRegion(center: CLLocationCoordinate2D(latitude: 48.8584, longitude: 2.2945), span: MKCoordinateSpan(latitudeDelta: 0.035, longitudeDelta: 0.035))
    @State private var selected: RiskPlace?
    @State private var showFullScreen = false
    private var displayedRisks: [RiskPlace] {
        guard let coordinate = store.location.coordinate else { return sampleRisks }
        let offsets = [(0.002, 0.002), (-0.002, 0.001), (0.001, -0.002)]
        return sampleRisks.enumerated().map { index, risk in
            let offset = offsets[index % offsets.count]
            return RiskPlace(id: risk.id, name: risk.name, category: risk.category, score: risk.score, summary: risk.summary, latitude: coordinate.latitude + offset.0, longitude: coordinate.longitude + offset.1, signals: risk.signals)
        }
    }
    var body: some View {
        NavigationStack {
            VStack(spacing: 0) {
                HStack { VStack(alignment: .leading) { Text("ZONE DE VIGILANCE").font(.caption.weight(.heavy)).tracking(1.2).foregroundStyle(TGColor.muted); Text("Carte des risques").font(.title.bold()) }; Spacer(); Label(store.location.city, systemImage: "location.fill").font(.caption.bold()).padding(9).background(.white).clipShape(Capsule()) }.padding(.horizontal, 20).padding(.top, 10).padding(.bottom, 12)
                Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: displayedRisks) { risk in MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) { Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(9).background(.white).clipShape(Circle()).shadow(radius: 3) } } }.frame(height: 260).clipShape(RoundedRectangle(cornerRadius: 22)).padding(.horizontal, 20).overlay(alignment: .bottomTrailing) { if store.location.coordinate == nil { Button { store.location.requestPermission() } label: { Label("Ma position", systemImage: "location.fill").font(.caption.bold()).padding(10).background(.white).clipShape(Capsule()) }.padding(12) } }.contentShape(Rectangle()).onTapGesture { showFullScreen = true }
                ScrollView { VStack(alignment: .leading, spacing: 10) { Text("Signaux à proximité").font(.title3.bold()).padding(.top, 16); ForEach(displayedRisks) { risk in Button { selected = risk } label: { HStack { Text("\(risk.score)").font(.headline.bold()).foregroundStyle(TGColor.coral).frame(width: 48, height: 48).background(TGColor.coral.opacity(0.1)).clipShape(Circle()); VStack(alignment: .leading) { Text(risk.name).font(.subheadline.bold()); Text("\(risk.category) · \(risk.summary)").font(.caption).foregroundStyle(TGColor.muted).lineLimit(2) }; Spacer(); Image(systemName: "chevron.right").foregroundStyle(TGColor.muted) }.foregroundStyle(TGColor.ink).padding(12).background(.white).clipShape(RoundedRectangle(cornerRadius: 16)) } } }.padding(.horizontal, 20).padding(.bottom, 24) }
            }.background(TGColor.ivory).navigationTitle("").navigationBarHidden(true).onAppear { store.location.refresh(); if let coordinate = store.location.coordinate { region.center = coordinate } }.onChange(of: store.location.city) { _, _ in if let coordinate = store.location.coordinate { region.center = coordinate } }
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
    var body: some View {
        NavigationStack {
            Map(coordinateRegion: $region, showsUserLocation: true, annotationItems: risks) { risk in
                MapAnnotation(coordinate: CLLocationCoordinate2D(latitude: risk.latitude, longitude: risk.longitude)) {
                    Button { selected = risk } label: { Image(systemName: "exclamationmark.triangle.fill").foregroundStyle(TGColor.coral).padding(10).background(.white).clipShape(Circle()).shadow(radius: 4) }
                }
            }
            .ignoresSafeArea()
            .toolbar { ToolbarItem(placement: .topBarLeading) { Button("Fermer") { dismiss() } } }
            .sheet(item: $selected) { risk in RiskDetailView(risk: risk) }
        }
    }
}

struct RiskDetailView: View { let risk: RiskPlace; var body: some View { VStack(alignment: .leading, spacing: 14) { Text(risk.category.uppercased()).font(.caption.bold()).foregroundStyle(TGColor.teal); Text(risk.name).font(.title.bold()); Text("Score de confiance : \(risk.score)/100").font(.headline); Text(risk.summary).foregroundStyle(TGColor.muted); ForEach(risk.signals, id: \.self) { signal in Text("• \(signal)") }; Spacer() }.padding(24).presentationDetents([.medium]) } }
