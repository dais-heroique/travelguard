import MapView, { Marker } from "react-native-maps";
import { StyleSheet } from "react-native";

import { scoreTone, type RiskPlace } from "@/lib/travelguard-data";

export function NativeRiskMap({ places, onSelect }: { places: RiskPlace[]; onSelect: (place: RiskPlace) => void }) {
  return (
    <MapView style={styles.map} initialRegion={{ latitude: 48.8584, longitude: 2.2945, latitudeDelta: 0.035, longitudeDelta: 0.035 }} showsUserLocation>
      {places.map((place) => <Marker key={place.id} coordinate={place.coordinate} pinColor={scoreTone(place.score).color} title={place.name} description={place.summary} onPress={() => onSelect(place)} />)}
    </MapView>
  );
}

const styles = StyleSheet.create({ map: { flex: 1 } });
