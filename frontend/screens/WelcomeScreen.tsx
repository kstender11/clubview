import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet, Image } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; // added this line

export default function WelcomeScreen({ navigation }: any) {
  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.top}>
          <Image
            source={require('../assets/clubview-icon.png')}
            style={styles.icon}
          />
          <Text style={styles.title}>ClubView</Text>
        </View>

        <View style={styles.bottom}>
          <Text style={styles.subtitle}>Discover the vibe{"\n"}before you arrive.</Text>

          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('Login')}
          >
            <Text style={styles.buttonText}>GET STARTED</Text>
          </TouchableOpacity>
        </View>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#000000', // background extends into notch area
  },
  container: {
    flex: 1,
    backgroundColor: '#000000',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingTop: 40,
    paddingHorizontal: 24,
  },
  top: {
    alignItems: 'center',
  },
  icon: {
    width: 400,
    height: 400,
    resizeMode: 'contain',
    marginBottom: -100, // move ClubView up
  },
  title: {
    fontSize: 64,
    color: '#9FDDE1',
    fontFamily: 'Literata_400Regular',
  },
  bottom: {
    alignItems: 'center',
    marginTop: 90, // pushes everything down a bit
  },
  subtitle: {
    color: '#FFFFFF',
    fontSize: 16,
    textAlign: 'center',
    fontFamily: 'Literata_400Regular',
    lineHeight: 24,
    marginBottom: 100, // creates space above button
  },
  button: {
    backgroundColor: '#9FDDE1',
    width: 218,
    height: 51,
    borderRadius: 50,
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: '#000000',
    fontWeight: 'bold',
    textTransform: 'uppercase',
    fontSize: 14,
  },
});
