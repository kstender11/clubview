import React, { createContext, useContext, useState } from 'react';

const CityContext = createContext({
  selectedCity: '',
  setSelectedCity: (city: string) => {},
});

export const CityProvider = ({ children }: any) => {
  const [selectedCity, setSelectedCity] = useState('');
  return (
    <CityContext.Provider value={{ selectedCity, setSelectedCity }}>
      {children}
    </CityContext.Provider>
  );
};

export const useCity = () => useContext(CityContext);
