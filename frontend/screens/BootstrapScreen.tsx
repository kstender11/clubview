import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import * as Location from 'expo-location';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCity } from './CityContext';

export default function BootstrapScreen({ navigation }: any) {
  const id = useRef(Math.random().toString(36).slice(2, 7));
  console.log('🌐 CityContext ID (Bootstrap)', id.current);

  const [phase, setPhase] = useState<'checking' | 'done'>('checking');
  const { setSelectedCity, setUserLocation } = useCity();

  useEffect(() => {
    (async () => {
      console.log('🔄 Bootstrap started…');

      const { status } = await Location.requestForegroundPermissionsAsync();
      console.log('📍 Location permission status:', status);

      if (status === 'granted') {
        try {
          const loc = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Highest,
          });
          console.log('📌 precise location', loc.coords);

          const coords = { lat: loc.coords.latitude, lng: loc.coords.longitude };
          setUserLocation(coords);
          console.log('📌 User location:', coords);

          const [place] = await Location.reverseGeocodeAsync(loc.coords);
          console.log('🧭 Reverse geocode result:', place);

          const fallbackCity = 'Los Angeles';
          const city = place.city || fallbackCity;

          setSelectedCity(city);
          await AsyncStorage.setItem('selectedCity', city);

          console.log('✅ Set city from GPS or fallback:', city);

          setPhase('done');
          navigation.replace('Home');
          return;
        } catch (err) {
          console.warn('⚠️ Reverse geocoding failed:', err);
        }
      }

      // Location denied or error
      const storedCity = await AsyncStorage.getItem('selectedCity');

      if (storedCity) {
        console.log(`✅ Found stored city: ${storedCity}`);
        const fallbackCoords: Record<string, { lat: number; lng: number }> = {
          'Los Angeles': { lat: 34.0522, lng: -118.2437 },
          'San Francisco': { lat: 37.7749, lng: -122.4194 },
          'Scottsdale': { lat: 33.4942, lng: -111.9261 },
        };
        setSelectedCity(storedCity);
        setUserLocation(fallbackCoords[storedCity] || fallbackCoords['Los Angeles']);
        navigation.replace('Home');
      } else {
        console.log('➡️ Navigating to CityPicker');
        navigation.replace('CityPicker');
      }

      setPhase('done');
    })();
  }, []);

  console.log('📦 Render phase:', phase);

  return (
    <View style={styles.center}>
      <ActivityIndicator size="large" color="#9FDDE1" />
      <Text style={styles.msg}>Getting your location…</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  center: {
    flex: 1,
    backgroundColor: '#000',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  msg: {
    color: '#FFF',
    fontFamily: 'Literata_400Regular',
    marginTop: 16,
    textAlign: 'center',
  },
});
