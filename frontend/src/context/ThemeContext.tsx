import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const THEME_STORAGE_KEY = '@ust_delivery_dark_mode';

interface Colors {
  background: string;
  surface: string;
  text: string;
  textSecondary: string;
  primary: string;
  accent: string;
  border: string;
  error: string;
  warning: string;
  success: string;
  shadow: string;
}

interface ThemeContextType {
  isDark: boolean;
  toggleTheme: () => void;
  colors: Colors;
}

const lightColors: Colors = {
  background: '#FFFFFF',
  surface: '#F5F5F5',
  text: '#1A1A1A',
  textSecondary: '#666666',
  primary: '#DA291C',
  accent: '#FFC72C',
  border: '#E0E0E0',
  error: '#DA291C',
  warning: '#FF9500',
  success: '#34C759',
  shadow: 'rgba(0, 0, 0, 0.1)',
};

const darkColors: Colors = {
  background: '#1A1A2E',
  surface: '#25274D',
  text: '#FFFFFF',
  textSecondary: '#B0B0B0',
  primary: '#FFC72C',
  accent: '#FFE66D',
  border: '#3A3A52',
  error: '#FF6B6B',
  warning: '#FFB84D',
  success: '#51CF66',
  shadow: 'rgba(0, 0, 0, 0.3)',
};

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [isDark, setIsDark] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadThemePreference();
  }, []);

  const loadThemePreference = async () => {
    try {
      const savedTheme = await AsyncStorage.getItem(THEME_STORAGE_KEY);
      if (savedTheme !== null) {
        setIsDark(savedTheme === 'dark');
      }
    } catch (error) {
      console.error('Failed to load theme preference:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTheme = async () => {
    const newTheme = !isDark;
    setIsDark(newTheme);
    try {
      await AsyncStorage.setItem(THEME_STORAGE_KEY, newTheme ? 'dark' : 'light');
    } catch (error) {
      console.error('Failed to save theme preference:', error);
    }
  };

  const colors = isDark ? darkColors : lightColors;

  if (isLoading) {
    return null;
  }

  return (
    <ThemeContext.Provider value={{ isDark, toggleTheme, colors }}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
