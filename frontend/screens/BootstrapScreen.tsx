import React, { useEffect, useState, useRef } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, TouchableOpacity } from 'react-native';
import * as Location from 'expo-location';
import { useCity } from './CityContext';

export default function BootstrapScreen({ navigation }: any) {
  // 🐞 DEBUG ───────────────────────────────────────────────────────
  const id = useRef(Math.random().toString(36).slice(2, 7));
  console.log('🌐 CityContext ID (Bootstrap)', id.current);
  //
  const [phase, setPhase] = useState<'checking' | 'denied' | 'done'>('checking');
  const { setSelectedCity, setUserLocation } = useCity();

  useEffect(() => {
    (async () => {
      console.log('🔄 Bootstrap started…');

      const { status } = await Location.requestForegroundPermissionsAsync();
      console.log('📍 Location permission status:', status);

      if (status === 'granted') {
        try {
          const loc = await Location.getCurrentPositionAsync({
            accuracy: Location.Accuracy.Highest,   // ⬅️ ask iOS/Android for precise fix
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
          console.log('✅ Set city from GPS or fallback:', city);

          setPhase('done');
          console.log('🚀 Navigating to Home...');
          navigation.replace('Home');
          return;
        } catch (err) {
          console.warn('⚠️ Reverse geocoding failed:', err);

          setSelectedCity('Los Angeles'); // fallback city
          setPhase('done');
          console.log('🛑 Using fallback city, navigating to Home...');
          navigation.replace('Home');
          return;
        }
      }

      console.log('❌ Location denied or error → show city picker');
      setPhase('denied');
    })();
  }, []);

  console.log('📦 Render phase:', phase);

  if (phase === 'checking') {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#9FDDE1" />
        <Text style={styles.msg}>Getting your location…</Text>
      </View>
    );
  }

  if (phase === 'denied') {
    return (
      <View style={styles.center}>
        <Text style={styles.msg}>Location services are off.</Text>
        <TouchableOpacity
          style={styles.btn}
          onPress={() => {
            console.log('➡️ Navigating to CityPicker');
            navigation.replace('CityPicker');
          }}
        >
          <Text style={styles.btnText}>Select City Manually</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Fallback UI if something weird happens
  return (
    <View style={styles.center}>
      <Text style={styles.msg}>Something went wrong…</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, backgroundColor: '#000', alignItems: 'center', justifyContent: 'center', padding: 24 },
  msg: { color: '#FFF', fontFamily: 'Literata_400Regular', marginTop: 16, textAlign: 'center' },
  btn: { backgroundColor: '#9FDDE1', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 30, marginTop: 24 },
  btnText: { color: '#000', fontWeight: 'bold' },
});
