import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useCity } from './CityContext'; // 🔑 import context hook

export default function CityPickerScreen({ navigation }: any) {
  const { setSelectedCity, setUserLocation } = useCity(); // ✅ include setUserLocation
  const cities = ['Los Angeles', 'Scottsdale', 'San Francisco'];

  // 🌍 Fallback coordinates for each city
  const fallbackCoords: Record<string, { lat: number; lng: number }> = {
    'Los Angeles':    { lat: 34.0522, lng: -118.2437 },
    'San Francisco':  { lat: 37.7749, lng: -122.4194 },
    'Scottsdale':     { lat: 33.4942, lng: -111.9261 },
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.inner}>
        <Text style={styles.title}>📍 Where are you partying?</Text>
        <Text style={styles.subtitle}>
          We couldn’t get your location. Choose a city to continue.
        </Text>

        {cities.map(city => (
          <TouchableOpacity
            key={city}
            style={styles.cityButton}
            onPress={() => {
              setSelectedCity(city);                     // ✅ save city
              setUserLocation(fallbackCoords[city]);     // ✅ set fallback coords
              navigation.replace('Home');                // ✅ go to Home
            }}
          >
            <Text style={styles.cityText}>📍 {city}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 24,
  },
  inner: {
    flexGrow: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingVertical: 60,
  },
  title: {
    color: '#FFF',
    fontSize: 28,
    fontFamily: 'Literata_400Regular',
    marginBottom: 12,
    textAlign: 'center',
  },
  subtitle: {
    color: '#AAA',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 32,
    paddingHorizontal: 12,
    fontFamily: 'Literata_400Regular',
    lineHeight: 22,
  },
  cityButton: {
    backgroundColor: '#9FDDE1',
    paddingVertical: 16,
    paddingHorizontal: 24,
    borderRadius: 30,
    width: '100%',
    alignItems: 'center',
    marginBottom: 16,
  },
  cityText: {
    fontSize: 18,
    fontWeight: '500',
    color: '#000',
  },
});
