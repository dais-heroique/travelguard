import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Location from "expo-location";
import * as Network from "expo-network";
import { useEffect, useMemo, useState } from "react";
import { Platform } from "react-native";

export type TravelLocation = {
  latitude: number;
  longitude: number;
  city: string;
  country: string;
};

export function useNetworkStatus() {
  const state = Network.useNetworkState();
  const isOnline = state.isInternetReachable ?? state.isConnected ?? false;
  const isChecking = state.isInternetReachable === null || state.isInternetReachable === undefined;
  return useMemo(() => ({ state, isOnline, isChecking }), [isChecking, isOnline, state]);
}

export function useTravelLocation() {
  const [location, setLocation] = useState<TravelLocation | null>(null);
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadLocation() {
      try {
        const cached = await AsyncStorage.getItem("@travelguard/last-location");
        if (cached && !cancelled) setLocation(JSON.parse(cached) as TravelLocation);
      } catch {
        // Ignore invalid or unavailable local cache.
      }

      if (Platform.OS === "web") {
        setIsLoading(false);
        return;
      }

      try {
        const servicesEnabled = await Location.hasServicesEnabledAsync();
        const permission = await Location.getForegroundPermissionsAsync();
        if (!servicesEnabled || !permission.granted) {
          if (!cancelled) {
            setPermissionDenied(true);
            setIsLoading(false);
          }
          return;
        }

        const current = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
        let city = "Position détectée";
        let country = "";
        try {
          const addresses = await Location.reverseGeocodeAsync({
            latitude: current.coords.latitude,
            longitude: current.coords.longitude,
          });
          const address = addresses[0];
          city = address?.city || address?.subregion || address?.region || city;
          country = address?.country || "";
        } catch {
          // Coordinates remain useful even when reverse geocoding is unavailable offline.
        }

        if (!cancelled) {
          const nextLocation = {
            latitude: current.coords.latitude,
            longitude: current.coords.longitude,
            city,
            country,
          };
          setLocation(nextLocation);
          await AsyncStorage.setItem("@travelguard/last-location", JSON.stringify(nextLocation));
          setPermissionDenied(false);
          setIsLoading(false);
        }
      } catch {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadLocation();
    return () => {
      cancelled = true;
    };
  }, []);

  return { location, permissionDenied, isLoading };
}

export function formatTravelPlace(location: TravelLocation | null) {
  if (!location) return "Position non disponible";
  return location.country ? `${location.city} · ${location.country}` : location.city;
}
