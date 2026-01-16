import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios, { AxiosError } from 'axios';
import Constants from 'expo-constants';
import { AppState } from 'react-native';

// Get API URL from environment or use default
const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || 
                process.env.EXPO_PUBLIC_BACKEND_URL || 
                'http://localhost:8000';

console.log('API_URL:', API_URL);

interface User {
  id: string;
  email: string;
  name: string;
  role: 'student' | 'organizer' | 'admin';
  college: string;
  department?: string;
  year?: number;
  organization_name?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  isLoggedIn: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [appState, setAppState] = useState(AppState.currentState);

  useEffect(() => {
    loadStoredAuth();
  }, []);

  // Listen for app state changes (background/foreground)
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => {
      subscription.remove();
    };
  }, []);

  const handleAppStateChange = async (state: AppState.AppStateStatus) => {
    setAppState(state);
    if (state === 'background') {
      console.log('[AuthContext] App moved to background - Auto-logging out user');
      // Auto-logout when app is closed/backgrounded
      try {
        await AsyncStorage.removeItem('token');
        await AsyncStorage.removeItem('user');
        setToken(null);
        setUser(null);
        console.log('[AuthContext] Auto-logout on background completed');
      } catch (error) {
        console.error('[AuthContext] Auto-logout error:', error);
      }
    } else if (state === 'active') {
      console.log('[AuthContext] App moved to foreground');
    }
  };

  const loadStoredAuth = async () => {
    try {
      const storedToken = await AsyncStorage.getItem('token');
      const storedUser = await AsyncStorage.getItem('user');
      
      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setError(null);
      console.log('Logging in with email:', email, 'API_URL:', API_URL);
      
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      }, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Login response:', response.data);
      const { access_token, user: userData } = response.data;
      
      await AsyncStorage.setItem('token', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      console.log('Login successful, user:', userData);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      setError(errorMessage);
      console.error('Login error - Type:', error.code, 'Message:', errorMessage, 'Response:', error.response?.status);
      throw new Error(errorMessage);
    }
  };

  const register = async (data: any) => {
    try {
      setError(null);
      console.log('Registering with email:', data.email, 'API_URL:', API_URL);
      
      const response = await axios.post(`${API_URL}/api/auth/register`, data, {
        timeout: 10000,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Register response:', response.data);
      const { access_token, user: userData } = response.data;
      
      await AsyncStorage.setItem('token', access_token);
      await AsyncStorage.setItem('user', JSON.stringify(userData));
      
      setToken(access_token);
      setUser(userData);
      console.log('Registration successful, user:', userData);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      setError(errorMessage);
      console.error('Register error - Type:', error.code, 'Message:', errorMessage, 'Response:', error.response?.status);
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    try {
      console.log('[AuthContext] Logout started');
      
      // Clear AsyncStorage FIRST
      await AsyncStorage.removeItem('token');
      await AsyncStorage.removeItem('user');
      console.log('[AuthContext] AsyncStorage cleared');
      
      // Clear state - this triggers the logout detection effect in index.tsx
      setToken(null);
      setUser(null);
      setError(null);
      console.log('[AuthContext] State cleared - logout complete');
      console.log('[AuthContext] User should now be null, triggering redirect to landing');
      
      return true;
    } catch (error) {
      console.error('[AuthContext] Logout error:', error);
      // Still clear state even if there's an error
      setToken(null);
      setUser(null);
      setError(null);
      throw error;
    }
  };

  const clearError = () => setError(null);

  const isLoggedIn = user !== null && token !== null;

  return (
    <AuthContext.Provider value={{ user, token, loading, error, login, register, logout, clearError, isLoggedIn }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useApi = () => {
  const { token } = useAuth();
  
  const api = axios.create({
    baseURL: `${API_URL}/api`,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
    },
  });

  api.interceptors.response.use(
    response => response,
    error => {
      if (error.response?.status === 401) {
        console.warn('Authentication failed - token may be expired');
      }
      return Promise.reject(error);
    }
  );

  return api;
};