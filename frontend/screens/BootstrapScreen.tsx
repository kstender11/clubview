import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet, TouchableOpacity } from 'react-native';
import * as Location from 'expo-location';

export default function BootstrapScreen({ navigation }: any) {
  const [phase, setPhase] = useState<'checking' | 'denied' | 'done'>('checking');

  useEffect(() => {
    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        /* optional: reverse-geocode here */
        navigation.replace('Home');   // coords can be passed as params
      } else {
        setPhase('denied');
      }
    })();
  }, []);

  if (phase === 'checking') {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#9FDDE1" />
        <Text style={styles.msg}>Getting your location…</Text>
      </View>
    );
  }

  /* denied → let user pick a city */
  return (
    <View style={styles.center}>
      <Text style={styles.msg}>Location services are off.</Text>
      <TouchableOpacity
        style={styles.btn}
        onPress={() => navigation.replace('CityPicker')}
      >
        <Text style={styles.btnText}>Select City Manually</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  center:{flex:1,backgroundColor:'#000',alignItems:'center',justifyContent:'center',padding:24},
  msg:{color:'#FFF',fontFamily:'Literata_400Regular',marginTop:16,textAlign:'center'},
  btn:{backgroundColor:'#9FDDE1',paddingHorizontal:24,paddingVertical:12,borderRadius:30,marginTop:24},
  btnText:{color:'#000',fontWeight:'bold'},
});
