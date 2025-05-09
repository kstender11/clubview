import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import WelcomeScreen   from './screens/WelcomeScreen';
import LoginScreen     from './screens/LoginScreen';
import SignUpScreen    from './screens/SignUpScreen';
import VerifyCodeScreen from './screens/VerifyCodeScreen';
import HomeScreen      from './screens/HomeScreen';
import { useFonts, Literata_400Regular } from '@expo-google-fonts/literata';
import AppLoading from 'expo-app-loading';

const Stack = createNativeStackNavigator();

export default function App() {
  const [fontsLoaded] = useFonts({ Literata_400Regular });
  if (!fontsLoaded) return <AppLoading />;

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Welcome" component={WelcomeScreen} />
        <Stack.Screen name="Login"   component={LoginScreen} />
        <Stack.Screen name="SignUp"  component={SignUpScreen} />
        <Stack.Screen name="Verify"  component={VerifyCodeScreen} />
        <Stack.Screen name="Home"    component={HomeScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
