import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define types for better type safety
type Location = { lat: number; lng: number } | null;

type CityContextType = {
  selectedCity: string;
  setSelectedCity: (city: string) => void;
  userLocation: Location;
  setUserLocation: (loc: Location) => void;
};

// Initial context value
const CityContext = createContext<CityContextType>({
  selectedCity: '',
  setSelectedCity: () => {},
  userLocation: null,
  setUserLocation: () => {},
});

type ProviderProps = {
  children: ReactNode;
};

export const CityProvider = ({ children }: ProviderProps) => {
  const [selectedCity, setSelectedCity] = useState('');
  const [userLocation, setUserLocation] = useState<Location>(null);

  return (
    <CityContext.Provider 
      value={{ 
        selectedCity, 
        setSelectedCity,
        userLocation,
        setUserLocation 
      }}
    >
      {children}
    </CityContext.Provider>
  );
};

export const useCity = () => useContext(CityContext);