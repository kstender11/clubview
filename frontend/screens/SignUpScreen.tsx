import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  TextInput,
  StyleSheet,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';

export default function SignUpScreen() {
  const navigation = useNavigation<any>();

  return (
    <SafeAreaView style={styles.container}>
      {/* Back Arrow */}
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backArrow}>←</Text>
      </TouchableOpacity>

      {/* Header */}
      <Text style={styles.header}>Create an Account</Text>

      {/* Content: Form, Divider, Socials, Footer */}
      <View style={styles.content}>
        {/* Form */}
        <View style={styles.form}>
          <TextInput
            placeholder="Username"
            placeholderTextColor="#999"
            style={styles.input}
          />
          <TextInput
            placeholder="Email"
            placeholderTextColor="#999"
            style={styles.input}
          />
          <TextInput
            placeholder="Phone Number"
            placeholderTextColor="#999"
            style={styles.input}
          />
          <TextInput
            placeholder="Password"
            placeholderTextColor="#999"
            secureTextEntry
            style={styles.input}
          />

          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('Verify')}
          >
            <Text style={styles.buttonText}>Sign Up</Text>
          </TouchableOpacity>
        </View>

        {/* Divider */}
        <View style={styles.dividerContainer}>
          <View style={styles.line} />
          <Text style={styles.orText}>OR</Text>
          <View style={styles.line} />
        </View>

        {/* Social Sign Up */}
        <View style={styles.socials}>
          <TouchableOpacity style={styles.socialButton}>
            <Image
              source={require('../assets/google-icon.png')}
              style={styles.socialIcon}
            />
            <Text style={styles.socialText}>Sign Up with Google</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.socialButton}>
            <Image
              source={require('../assets/apple-icon.png')}
              style={styles.socialIcon}
            />
            <Text style={styles.socialText}>Sign Up with Apple</Text>
          </TouchableOpacity>
        </View>

        {/* Footer */}
        <Text style={styles.footerText}>
          Join the party and discover{'\n'}where the night’s headed.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const FIXED_WIDTH = 310;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  backButton: {
    alignSelf: 'flex-start',
    marginTop: 10,
  },
  backArrow: {
    color: '#FFF',
    fontSize: 28,
    marginLeft: 5,
  },
  header: {
    fontSize: 32,
    color: '#FFF',
    fontFamily: 'Literata_400Regular',
    marginTop: 40,
    marginBottom: 20,
  },
  content: {
    marginTop: 40,
    alignItems: 'center',
  },
  form: {
    width: FIXED_WIDTH,
    alignItems: 'center',
  },
  input: {
    width: '100%',
    backgroundColor: '#222',
    color: '#FFF',
    borderRadius: 30,
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginBottom: 16,
    fontSize: 16,
    fontFamily: 'Literata_400Regular',
  },
  button: {
    backgroundColor: '#9FDDE1',
    borderRadius: 30,
    width: '100%',
    height: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 12,
  },
  buttonText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 16,
  },
  dividerContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 28,
    width: FIXED_WIDTH,
  },
  line: {
    flex: 1,
    height: 1,
    backgroundColor: '#888',
  },
  orText: {
    color: '#FFF',
    marginHorizontal: 12,
    fontFamily: 'Literata_400Regular',
  },
  socials: {
    width: FIXED_WIDTH,
    alignItems: 'center',
    gap: 16,
  },
  socialButton: {
    flexDirection: 'row',
    backgroundColor: '#FFF',
    borderRadius: 30,
    width: 220, // match LoginScreen button width
    height: 48,
    alignItems: 'center',
    justifyContent: 'center',
    paddingLeft: 18,
  },
  socialIcon: {
    width: 20,
    height: 20,
    marginRight: 12,
    position: 'absolute',
    left: 18,
  },
  socialText: {
    color: '#000',
    fontSize: 16,
    fontFamily: 'Literata_400Regular',
  },
  footerText: {
    color: '#FFF',
    fontSize: 14,
    marginTop: 60,
    marginBottom: 30,
    textAlign: 'center',
    fontFamily: 'Literata_400Regular',
  },
});
