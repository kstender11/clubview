import React, { useEffect, useState, useCallback } from 'react';
import {
  View, Text, StyleSheet, Image, TouchableOpacity,
  ActivityIndicator, useWindowDimensions, FlatList, RefreshControl
} from 'react-native';
import { SafeAreaView, useSafeAreaInsets } from 'react-native-safe-area-context';
import { useCity } from './CityContext';
import { API_BASE_URL } from '@env';

interface Venue {
  id: string;
  name: string;
  distance: number;
  categories?: string[];
}

const API_URL = `${API_BASE_URL}/api/venues/discover`;
const PAGE_SIZE = 10;

export default function HomeScreen() {
  const { selectedCity, userLocation } = useCity();
  const [venues, setVenues] = useState<Venue[]>([]);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);

  const { width } = useWindowDimensions();
  const insets = useSafeAreaInsets();
  const CARD_W = width - 48;
  const COMPACT_H = 120;

  const fetchVenues = useCallback(async (pageNum = 0, isRefreshing = false) => {
    if (!userLocation || loading) return;
    
    setLoading(true);
    if (isRefreshing) setRefreshing(true);

    try {
      const url = `${API_URL}?city=${selectedCity}&lat=${userLocation.lat}&lng=${userLocation.lng}&radius=50000&skip=${pageNum * PAGE_SIZE}&limit=${PAGE_SIZE}`;
      const response = await fetch(url);
      const data: Venue[] = await response.json();

      if (data.length < PAGE_SIZE) setHasMore(false);
      
      if (isRefreshing || pageNum === 0) {
        setVenues(data);
      } else {
        setVenues(prev => [...prev, ...data]);
      }
      setPage(pageNum);
    } catch (error) {
      console.error('Failed to fetch venues:', error);
    } finally {
      setLoading(false);
      if (isRefreshing) setRefreshing(false);
    }
  }, [userLocation, selectedCity, loading]);

  useEffect(() => {
    if (userLocation) fetchVenues(0);
  }, [userLocation, selectedCity]);

  const onRefresh = useCallback(() => {
    setHasMore(true);
    fetchVenues(0, true);
  }, [fetchVenues]);

  const loadMore = useCallback(() => {
    if (!loading && hasMore) {
      fetchVenues(page + 1);
    }
  }, [loading, hasMore, page, fetchVenues]);

  const renderItem = ({ item }: { item: Venue }) => (
    <TouchableOpacity
      key={item.id}
      activeOpacity={0.85}
      style={[styles.compactCard, { width: CARD_W, height: COMPACT_H }]}
    >
      <Image 
        source={require('../assets/sample1.jpg')}
        style={[styles.compactImage, { height: COMPACT_H }]} 
      />
      <View style={styles.compactInfo}>
        <Text style={styles.compactName}>{item.name}</Text>
        <Text style={styles.compactDistance}>{(item.distance / 1609).toFixed(1)} mi</Text>
        <View style={styles.tagRow}>
          {(item.categories || []).slice(0,3).map((tag: string) => (
            <View key={tag} style={styles.tagChipSmall}>
              <Text style={styles.tagTextSmall}>{tag.toUpperCase()}</Text>
            </View>
          ))}
        </View>
      </View>
    </TouchableOpacity>
  );

  if (!userLocation) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#9FDDE1" />
        <Text style={{ color:'#9FDDE1', marginTop:12 }}>Getting your location...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={venues}
        renderItem={renderItem}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{
          paddingTop: insets.top + 8,
          paddingBottom: 32,
          paddingHorizontal: 24
        }}
        ListHeaderComponent={
          <>
            <Text style={styles.h2}>Nearby</Text>
          </>
        }
        ListEmptyComponent={
          !loading ? (
            <Text style={styles.info}>No spots within 30 mi of {selectedCity} yet.</Text>
          ) : null
        }
        ListFooterComponent={
          loading && !refreshing && venues.length > 0 ? (
            <ActivityIndicator size="small" color="#9FDDE1" style={{ marginVertical: 20 }} />
          ) : null
        }
        onEndReached={loadMore}
        onEndReachedThreshold={0.5}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#9FDDE1"
            colors={['#9FDDE1']}
          />
        }
        showsVerticalScrollIndicator={false}
      />
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
