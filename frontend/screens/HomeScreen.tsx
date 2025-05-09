import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, Image, ScrollView, TouchableOpacity,
  ActivityIndicator, useWindowDimensions,
} from 'react-native';
import * as Location from 'expo-location';
import AsyncStorage  from '@react-native-async-storage/async-storage';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import Feather  from 'react-native-vector-icons/Feather';
import Ionicons from 'react-native-vector-icons/Ionicons';

/* ——— static sample data ——— */
const filters = [
  { label: 'Trending',  icon: 'flame' },
  { label: 'Cocktails', icon: 'wine'  },
  { label: 'Music',     icon: 'musical-notes' },
];

const heroPick = {
  name : 'Bar Lis',
  image: require('../assets/sample-hero.jpg'),
  tags : ['Lively', 'Trendy'],
};

const nearby = [
  { id:'1', name:'Roccos',    image:require('../assets/sample1.jpg'), distance:'0.4 mi', tags:['Lively','Dancing'] },
  { id:'2', name:'Wolfsglen', image:require('../assets/sample2.jpg'), distance:'0.2 mi', tags:['Chill','Cocktails'] },
  { id:'3', name:'Poppy',     image:require('../assets/sample3.jpg'), distance:'2.6 mi', tags:['DJ','Dancing'] },
];
/* ———————————————————————— */

export default function HomeScreen() {
  const [phase, setPhase] = useState<'checking' | 'denied' | 'granted'>('checking');
  const { width }   = useWindowDimensions();
  const insets      = useSafeAreaInsets();
  const CARD_WIDTH  = width - 48;
  const HERO_H      = CARD_WIDTH * 0.6;
  const COMPACT_H   = 120;

  /* ask for permission (runs once) */
  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        setPhase('granted');
      } else {
        const manual = await AsyncStorage.getItem('manualCity');
        setPhase(manual ? 'granted' : 'denied');
      }
    })();
  }, []);

  /* ——— 1. spinner while checking ——— */
  if (phase === 'checking') {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#9FDDE1" />
      </View>
    );
  }

  /* ——— 2. fallback picker when denied & no saved city ——— */
  if (phase === 'denied') {
    return (
      <SafeAreaView style={styles.safeArea}>
        <ScrollView contentContainerStyle={styles.inner}>
          <Text style={styles.h1}>📍 Where are you partying?</Text>
          <Text style={styles.info}>
            We couldn’t get your location. Choose a city to continue.
          </Text>

          {['Los Angeles', 'Scottsdale', 'San Francisco'].map(city => (
            <TouchableOpacity
              key={city}
              style={styles.cityBtn}
              onPress={async () => {
                await AsyncStorage.setItem('manualCity', city);
                setPhase('granted');           // re-render feed
              }}
            >
              <Text style={styles.cityTxt}>📍 {city}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </SafeAreaView>
    );
  }

  /* ——— 3. permission OK → render the real feed ——— */
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        style={styles.container}
        contentContainerStyle={{ paddingTop: insets.top + 8, paddingBottom: 32 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Title */}
        <Text style={[styles.h1, { marginTop: 8 }]}>Tonight’s Top Picks</Text>

        {/* Filter row */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterRow}>
          {filters.map(f => (
            <View key={f.label} style={styles.chip}>
              <Ionicons name={f.icon} size={14} color="#9FDDE1" />
              <Text style={styles.chipLabel}>{f.label}</Text>
            </View>
          ))}
          <View style={styles.filterChip}>
            <Feather name="sliders" size={16} color="#000" />
            <Text style={styles.filterLabel}>Filters</Text>
          </View>
        </ScrollView>

        {/* Hero card */}
        <TouchableOpacity
          activeOpacity={0.85}
          style={[styles.heroCard, { width: CARD_WIDTH, height: HERO_H }]}
        >
          <Image source={heroPick.image} style={styles.heroImage} />
          <View style={styles.heroOverlay}>
            <Text style={styles.heroTitle}>{heroPick.name.toUpperCase()}</Text>
            <View style={styles.tagRow}>
              {heroPick.tags.map(tag => (
                <View key={tag} style={styles.tagChip}>
                  <Text style={styles.tagText}>{tag.toUpperCase()}</Text>
                </View>
              ))}
            </View>
          </View>
        </TouchableOpacity>

        {/* Nearby */}
        <Text style={styles.h2}>Nearby</Text>

        {nearby.map(item => (
          <TouchableOpacity
            key={item.id}
            activeOpacity={0.85}
            style={[styles.compactCard, { width: CARD_WIDTH, height: COMPACT_H }]}
          >
            <Image source={item.image} style={[styles.compactImage, { height: COMPACT_H }]} />
            <View style={styles.compactInfo}>
              <Text style={styles.compactName}>{item.name}</Text>
              <Text style={styles.compactDistance}>{item.distance}</Text>
              <View style={styles.tagRow}>
                {item.tags.map(t => (
                  <View key={t} style={styles.tagChipSmall}>
                    <Text style={styles.tagTextSmall}>{t.toUpperCase()}</Text>
                  </View>
                ))}
              </View>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

/* ——— styles ——— */
const styles = StyleSheet.create({
  safeArea:{ flex:1, backgroundColor:'#000' },
  container:{ flex:1, backgroundColor:'#000', paddingHorizontal:24 },
  loading:{ flex:1, justifyContent:'center', alignItems:'center', backgroundColor:'#000' },

  /* fallback */
  inner:{ flexGrow:1, justifyContent:'center', alignItems:'center', paddingVertical:60 },
  info:{ color:'#AAA', fontSize:15, textAlign:'center', marginBottom:24, fontFamily:'Literata_400Regular' },
  cityBtn:{ backgroundColor:'#9FDDE1', borderRadius:30, paddingVertical:12, paddingHorizontal:40, marginBottom:16 },
  cityTxt:{ color:'#000', fontSize:16, fontWeight:'600' },

  /* typography */
  h1:{ color:'#FFF', fontSize:32, fontFamily:'Literata_400Regular', marginBottom:12 },
  h2:{ color:'#FFF', fontSize:28, fontFamily:'Literata_400Regular', marginVertical:20 },

  /* chips */
  filterRow:{ gap:12, paddingVertical:8 },
  chip:{ flexDirection:'row', backgroundColor:'#222', borderRadius:20, paddingHorizontal:14, paddingVertical:6, alignItems:'center' },
  chipLabel:{ color:'#9FDDE1', marginLeft:6, fontSize:14 },
  filterChip:{ flexDirection:'row', backgroundColor:'#9FDDE1', borderRadius:20, paddingHorizontal:16, paddingVertical:6, alignItems:'center' },
  filterLabel:{ color:'#000', marginLeft:6, fontSize:14, fontWeight:'600' },

  /* hero */
  heroCard:{ borderRadius:12, overflow:'hidden', marginVertical:12 },
  heroImage:{ width:'100%', height:'100%' },
  heroOverlay:{ ...StyleSheet.absoluteFillObject, justifyContent:'flex-end', padding:16 },
  heroTitle:{ color:'#FFF', fontSize:24, fontFamily:'Literata_400Regular' },
  tagRow:{ flexDirection:'row', gap:8, marginTop:4 },
  tagChip:{ backgroundColor:'#444', borderRadius:14, paddingHorizontal:10, paddingVertical:4 },
  tagText:{ color:'#9FDDE1', fontSize:12 },

  /* nearby cards */
  compactCard:{ backgroundColor:'#1C1C1E', borderRadius:16, flexDirection:'row', alignItems:'center', marginBottom:18 },
  compactImage:{ width:120, resizeMode:'cover' },
  compactInfo:{ flex:1, paddingHorizontal:14, paddingVertical:10 },
  compactName:{ color:'#FFF', fontSize:20, fontFamily:'Literata_400Regular' },
  compactDistance:{ color:'#AAA', fontSize:12, marginTop:2 },
  tagChipSmall:{ backgroundColor:'#444', borderRadius:12, paddingHorizontal:8, paddingVertical:2, marginRight:6, marginTop:6 },
  tagTextSmall:{ color:'#9FDDE1', fontSize:10 },
});
