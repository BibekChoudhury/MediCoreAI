import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import {
  clearStoredToken,
  fetchProfile,
  getStoredToken,
  loginUser,
  logoutUser,
  registerUser,
  storeToken,
} from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);

  async function refreshProfile() {
    const profile = await fetchProfile();
    setUser(profile);
    return profile;
  }

  useEffect(() => {
    async function initializeAuth() {
      const token = getStoredToken();
      if (!token) {
        setIsInitializing(false);
        return;
      }

      try {
        await refreshProfile();
      } catch {
        clearStoredToken();
        setUser(null);
      } finally {
        setIsInitializing(false);
      }
    }

    initializeAuth();
  }, []);

  async function login({ email, password, rememberMe }) {
    const data = await loginUser({
      email,
      password,
      remember_me: rememberMe,
    });

    storeToken(data.access_token, rememberMe);
    return refreshProfile();
  }

  async function register(payload) {
    return registerUser(payload);
  }

  async function logout() {
    try {
      await logoutUser();
    } catch {
      // Logout is client-side token invalidation for this JWT implementation.
    } finally {
      clearStoredToken();
      setUser(null);
    }
  }

  const value = useMemo(
    () => ({
      user,
      isInitializing,
      isAuthenticated: Boolean(user),
      login,
      register,
      logout,
      refreshProfile,
      setUser,
    }),
    [user, isInitializing],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
