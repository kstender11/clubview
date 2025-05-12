import React, { useEffect } from 'react';
import * as SplashScreen from 'expo-splash-screen';
import { useFonts, Literata_400Regular } from '@expo-google-fonts/literata';
import { CityProvider } from './screens/CityContext';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

// Screens
import WelcomeScreen from './screens/WelcomeScreen';
import LoginScreen from './screens/LoginScreen';
import SignUpScreen from './screens/SignUpScreen';
import VerifyCodeScreen from './screens/VerifyCodeScreen';
import HomeScreen from './screens/HomeScreen';
import BootstrapScreen from './screens/BootstrapScreen';
import CityPickerScreen from './screens/CityPickerScreen';

const Stack = createNativeStackNavigator();

SplashScreen.preventAutoHideAsync();

export default function App() {
  const [fontsLoaded] = useFonts({ Literata_400Regular });

  useEffect(() => {
    if (fontsLoaded) SplashScreen.hideAsync();
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return (
    <CityProvider>
      <NavigationContainer>
        <Stack.Navigator
          initialRouteName="Welcome" // 👈 Change this to test different screens
          screenOptions={{ headerShown: false }}
        >
          <Stack.Screen name="Bootstrap" component={BootstrapScreen} />
          <Stack.Screen name="CityPicker" component={CityPickerScreen} />
          <Stack.Screen name="Home" component={HomeScreen} />
          <Stack.Screen name="Welcome" component={WelcomeScreen} />
          <Stack.Screen name="Login" component={LoginScreen} />
          <Stack.Screen name="SignUp" component={SignUpScreen} />
          <Stack.Screen name="Verify" component={VerifyCodeScreen} />
        </Stack.Navigator>
      </NavigationContainer>
    </CityProvider>
  );
}
