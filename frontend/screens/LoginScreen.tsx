import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Image,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Feather from 'react-native-vector-icons/Feather';

export default function LoginScreen({ navigation }: any) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [secureText, setSecureText] = useState(true);
  const [error, setError] = useState('');

  const handleNext = () => {
    if (!email.includes('@')) {
      setError('Please enter a valid email address.');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    setError('');
    navigation.navigate('Bootstrap'); // Adjust this as needed
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.top}>
        <Image
          source={require('../assets/clubview-logo.png')}
          style={styles.icon}
        />
        <Text style={styles.header}>Log In</Text>
      </View>

      <View style={styles.form}>
        <TextInput
          placeholder="Email or Username"
          placeholderTextColor="#999"
          style={styles.input}
          value={email}
          onChangeText={setEmail}
        />

        <View style={styles.passwordWrapper}>
          <TextInput
            placeholder="Password"
            placeholderTextColor="#999"
            secureTextEntry={secureText}
            style={styles.passwordInput}
            value={password}
            onChangeText={setPassword}
          />
          <TouchableOpacity onPress={() => setSecureText(!secureText)}>
            <Feather
              name={secureText ? 'eye' : 'eye-off'}
              size={20}
              color="#FFF"
            />
          </TouchableOpacity>
        </View>

        {error ? <Text style={styles.error}>{error}</Text> : null}

        <TouchableOpacity style={styles.button} onPress={handleNext}>
          <Text style={styles.buttonText}>Next</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.dividerContainer}>
        <View style={styles.line} />
        <Text style={styles.orText}>OR</Text>
        <View style={styles.line} />
      </View>

      <View style={styles.socials}>
        <TouchableOpacity style={styles.socialButton}>
          <Image
            source={require('../assets/google-icon.png')}
            style={styles.socialIcon}
          />
          <Text style={styles.socialText}>Log in with Google</Text>
        </TouchableOpacity>

        <TouchableOpacity style={styles.socialButton}>
          <Image
            source={require('../assets/apple-icon.png')}
            style={styles.socialIcon}
          />
          <Text style={styles.socialText}>Log in with Apple</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.footerText}>
        Don’t have an account with us?{' '}
        <Text style={styles.signUp} onPress={() => navigation.navigate('SignUp')}>
          Sign Up
        </Text>
      </Text>
    </SafeAreaView>
  );
}

const FIXED_WIDTH = 310;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'flex-start',
  },
  top: {
    alignItems: 'center',
    marginTop: 0,
    marginBottom: -10,
  },
  icon: {
    width: 400,
    height: 400,
    resizeMode: 'contain',
    marginBottom: -130,
  },
  header: {
    color: '#FFF',
    fontSize: 36,
    fontFamily: 'Literata_400Regular',
    marginBottom: 40,
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
  passwordWrapper: {
    width: '100%',
    backgroundColor: '#222',
    borderRadius: 30,
    paddingHorizontal: 20,
    paddingVertical: 0,
    marginBottom: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  passwordInput: {
    flex: 1,
    paddingVertical: 12,
    color: '#FFF',
    fontSize: 16,
    fontFamily: 'Literata_400Regular',
  },
  error: {
    color: 'red',
    fontSize: 14,
    marginBottom: 8,
    marginTop: -8,
    alignSelf: 'flex-start',
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
    width: 220,
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
    marginTop: 32,
    fontFamily: 'Literata_400Regular',
  },
  signUp: {
    color: '#9FDDE1',
    fontWeight: '600',
  },
});
