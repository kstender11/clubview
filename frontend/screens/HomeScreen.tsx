import React, { useEffect, useState, useRef } from 'react';
import {
  View, Text, StyleSheet, Image, ScrollView, TouchableOpacity,
  ActivityIndicator, useWindowDimensions,
} from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import Feather from 'react-native-vector-icons/Feather';
import Ionicons from 'react-native-vector-icons/Ionicons';
import { useCity } from './CityContext';
import { API_BASE_URL } from '@env';

const filters = [ /* … same … */ ];
const heroPick  = { /* … same … */ };
const API_URL = `${API_BASE_URL}/api/venues/discover`;

export default function HomeScreen() {
  const { selectedCity, userLocation } = useCity();
  const [venues,  setVenues]  = useState([]);
  const [loading, setLoading] = useState(false);

  const { width }  = useWindowDimensions();
  const insets     = useSafeAreaInsets();
  const CARD_W     = width - 48;
  const HERO_H     = CARD_W * 0.6;
  const COMPACT_H  = 120;

  /* fetch when we have coords */
  useEffect(() => {
    if (!userLocation) return;         // still waiting for coords (GPS or fallback)
      console.log('📍 userLocation =', userLocation);
    setLoading(true);

    const url = `${API_URL}?city=${selectedCity}&lat=${userLocation.lat}&lng=${userLocation.lng}&radius=50000`;
    console.log('📡', url);

    fetch(url)
      .then(r => r.json())
      .then(setVenues)
      .catch(err => {
        console.error('❌ fetch', err);
        setVenues([]);
      })
      .finally(() => setLoading(false));
  }, [userLocation]);

  /* spinner while coords or data pending */
  if (!userLocation || loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#9FDDE1" />
        <Text style={{ color:'#9FDDE1', marginTop:12 }}>Loading venues…</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }}
        showsVerticalScrollIndicator={false}
      >
        {/* top picks, filters … */}

        <Text style={styles.h2}>Nearby</Text>

        {venues.length === 0 ? (
          <Text style={styles.info}>No spots within 4 km of {selectedCity} yet.</Text>
        ) : (
          venues.map((v: any) => (
            <TouchableOpacity
              key={v.id}
              activeOpacity={0.85}
              style={[styles.compactCard, { width: CARD_W, height: COMPACT_H }]}
            >
              <Image source={require('../assets/sample1.jpg')}
                     style={[styles.compactImage, { height: COMPACT_H }]} />
              <View style={styles.compactInfo}>
                <Text style={styles.compactName}>{v.name}</Text>
                <Text style={styles.compactDistance}>{(v.distance / 1609).toFixed(1)} mi</Text>
                <View style={styles.tagRow}>
                  {(v.categories || []).slice(0,3).map((tag:string) => (
                    <View key={tag} style={styles.tagChipSmall}>
                      <Text style={styles.tagTextSmall}>{tag.toUpperCase()}</Text>
                    </View>
                  ))}
                </View>
              </View>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}


const styles = StyleSheet.create({
  safeArea:{ flex:1, backgroundColor:'#000' },
  container:{ flex:1, backgroundColor:'#000', paddingHorizontal:24 },
  loading:{ flex:1, justifyContent:'center', alignItems:'center', backgroundColor:'#000' },
  inner:{ flexGrow:1, justifyContent:'center', alignItems:'center', paddingVertical:60 },
  info:{ color:'#AAA', fontSize:15, textAlign:'center', marginBottom:24, fontFamily:'Literata_400Regular' },
  cityBtn:{ backgroundColor:'#9FDDE1', borderRadius:30, paddingVertical:12, paddingHorizontal:40, marginBottom:16 },
  cityTxt:{ color:'#000', fontSize:16, fontWeight:'600' },
  h1:{ color:'#FFF', fontSize:32, fontFamily:'Literata_400Regular', marginBottom:12 },
  h2:{ color:'#FFF', fontSize:28, fontFamily:'Literata_400Regular', marginVertical:20 },
  filterRow:{ gap:12, paddingVertical:8 },
  chip:{ flexDirection:'row', backgroundColor:'#222', borderRadius:20, paddingHorizontal:14, paddingVertical:6, alignItems:'center' },
  chipLabel:{ color:'#9FDDE1', marginLeft:6, fontSize:14 },
  filterChip:{ flexDirection:'row', backgroundColor:'#9FDDE1', borderRadius:20, paddingHorizontal:16, paddingVertical:6, alignItems:'center' },
  filterLabel:{ color:'#000', marginLeft:6, fontSize:14, fontWeight:'600' },
  heroCard:{ borderRadius:12, overflow:'hidden', marginVertical:12 },
  heroImage:{ width:'100%', height:'100%' },
  heroOverlay:{ ...StyleSheet.absoluteFillObject, justifyContent:'flex-end', padding:16 },
  heroTitle:{ color:'#FFF', fontSize:24, fontFamily:'Literata_400Regular' },
  tagRow:{ flexDirection:'row', gap:8, marginTop:4 },
  tagChip:{ backgroundColor:'#444', borderRadius:14, paddingHorizontal:10, paddingVertical:4 },
  tagText:{ color:'#9FDDE1', fontSize:12 },
  compactCard:{ backgroundColor:'#1C1C1E', borderRadius:16, flexDirection:'row', alignItems:'center', marginBottom:18 },
  compactImage:{ width:120, resizeMode:'cover' },
  compactInfo:{ flex:1, paddingHorizontal:14, paddingVertical:10 },
  compactName:{ color:'#FFF', fontSize:20, fontFamily:'Literata_400Regular' },
  compactDistance:{ color:'#AAA', fontSize:12, marginTop:2 },
  tagChipSmall:{ backgroundColor:'#444', borderRadius:12, paddingHorizontal:8, paddingVertical:2, marginRight:6, marginTop:6 },
  tagTextSmall:{ color:'#9FDDE1', fontSize:10 },
});
