import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function VerifyCodeScreen({ navigation }: any) {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleVerify = () => {
    if (code.length !== 6 || !/^[0-9]{6}$/.test(code)) {
      setError('Please enter a valid 6-digit code.');
      return;
    }
    setError('');
    navigation.navigate('Home'); // Replace with actual destination later
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Back Arrow */}
      <TouchableOpacity style={styles.backButton} onPress={() => navigation.goBack()}>
        <Text style={styles.backArrow}>←</Text>
      </TouchableOpacity>

      <Text style={styles.title}>Enter Verification Code</Text>
      <Text style={styles.subtitle}>We sent a 6-digit code to your phone/email.</Text>

      <TextInput
        value={code}
        onChangeText={setCode}
        keyboardType="number-pad"
        maxLength={6}
        placeholder="123456"
        placeholderTextColor="#888"
        style={styles.input}
      />

      {error ? <Text style={styles.error}>{error}</Text> : null}

      <TouchableOpacity style={styles.button} onPress={handleVerify}>
        <Text style={styles.buttonText}>Verify</Text>
      </TouchableOpacity>

      <Text style={styles.footer}>
        Didn’t receive a code?{' '}
        <Text style={styles.resend}>Resend</Text>
      </Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    paddingHorizontal: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  backButton: {
    position: 'absolute',
    top: 110,
    left: 40,
  },
  backArrow: {
    color: '#FFF',
    fontSize: 28,
  },
  title: {
    color: '#FFF',
    fontSize: 28,
    fontFamily: 'Literata_400Regular',
    marginBottom: 12,
  },
  subtitle: {
    color: '#AAA',
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 30,
    fontFamily: 'Literata_400Regular',
  },
  input: {
    backgroundColor: '#222',
    color: '#FFF',
    borderRadius: 30,
    paddingVertical: 12,
    paddingHorizontal: 20,
    fontSize: 20,
    textAlign: 'center',
    letterSpacing: 6,
    width: 200,
  },
  error: {
    color: 'red',
    fontSize: 14,
    marginTop: 8,
    fontFamily: 'Literata_400Regular',
  },
  button: {
    backgroundColor: '#9FDDE1',
    borderRadius: 30,
    width: 200,
    height: 48,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 24,
  },
  buttonText: {
    color: '#000',
    fontWeight: 'bold',
    fontSize: 16,
  },
  footer: {
    color: '#FFF',
    marginTop: 24,
    fontSize: 14,
    fontFamily: 'Literata_400Regular',
  },
  resend: {
    color: '#9FDDE1',
    fontWeight: '600',
  },
});
