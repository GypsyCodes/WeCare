import React, { createContext, useContext, useState, useEffect } from 'react';

// Create the context
const ThemeContext = createContext();

// Create a custom hook to use the theme context
export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Theme provider component
export const ThemeProvider = ({ children }) => {
  // Get initial theme from localStorage or default to light
  const [theme, setTheme] = useState(() => {
    const savedTheme = localStorage.getItem('we-care-theme');
    return savedTheme || 'light';
  });

  // Update theme and save to localStorage
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('we-care-theme', newTheme);
  };

  const setLightTheme = () => {
    setTheme('light');
    localStorage.setItem('we-care-theme', 'light');
  };

  const setDarkTheme = () => {
    setTheme('dark');
    localStorage.setItem('we-care-theme', 'dark');
  };

  // Update CSS variables based on theme
  useEffect(() => {
    const root = document.documentElement;
    
    // Set We Care brand colors
    root.style.setProperty('--we-care-primary', '#429E17');
    root.style.setProperty('--we-care-primary-dark', '#2D6E0A');
    root.style.setProperty('--we-care-white', '#FFFFFF');
    root.style.setProperty('--we-care-primary-light', 'rgba(66, 158, 23, 0.1)');
    
    // Override Bootstrap primary colors with We Care green
    root.style.setProperty('--bs-primary', '#429E17');
    root.style.setProperty('--bs-primary-rgb', '66, 158, 23');
    
    if (theme === 'dark') {
      root.style.setProperty('--bs-body-bg', '#121212');
      root.style.setProperty('--bs-body-color', '#ffffff');
      root.style.setProperty('--bs-card-bg', '#1e1e1e');
      root.style.setProperty('--bs-border-color', '#333333');
      root.style.setProperty('--bs-gray-100', '#2d2d2d');
      root.style.setProperty('--bs-gray-200', '#3a3a3a');
      root.style.setProperty('--bs-gray-300', '#4a4a4a');
      root.setAttribute('data-bs-theme', 'dark');
      document.body.classList.add('dark-theme');
      document.body.classList.remove('light-theme');
    } else {
      root.style.setProperty('--bs-body-bg', '#ffffff');
      root.style.setProperty('--bs-body-color', '#212529');
      root.style.setProperty('--bs-card-bg', '#ffffff');
      root.style.setProperty('--bs-border-color', '#dee2e6');
      root.style.setProperty('--bs-gray-100', '#f8f9fa');
      root.style.setProperty('--bs-gray-200', '#e9ecef');
      root.style.setProperty('--bs-gray-300', '#dee2e6');
      root.setAttribute('data-bs-theme', 'light');
      document.body.classList.add('light-theme');
      document.body.classList.remove('dark-theme');
    }
  }, [theme]);

  const value = {
    theme,
    toggleTheme,
    setLightTheme,
    setDarkTheme,
    isDark: theme === 'dark',
    isLight: theme === 'light'
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}; 