"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { auth, users, User } from "./api";

function _setTokens(access: string, refresh: string) {
  localStorage.setItem("nexus_access_token", access);
  localStorage.setItem("nexus_refresh_token", refresh);
}
function _clearTokens() {
  localStorage.removeItem("nexus_access_token");
  localStorage.removeItem("nexus_refresh_token");
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  loginAsGuest: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 5_000);
    const token = typeof window !== "undefined"
      ? localStorage.getItem("nexus_access_token")
      : null;

    if (token) {
      users.me()
        .then(setUser)
        .catch(() => {
          // Token invalid or expired and refresh failed — clear and treat as logged out.
          _clearTokens();
        })
        .finally(() => { clearTimeout(timer); setLoading(false); });
    } else {
      clearTimeout(timer);
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { access_token, refresh_token } = await auth.login(email, password);
    _setTokens(access_token, refresh_token);
    try { setUser(await users.me()); }
    catch { setUser({ id: "", email, full_name: null, is_active: true, is_verified: false }); }
  };

  const register = async (email: string, password: string, name?: string) => {
    const { access_token, refresh_token } = await auth.register(email, password, name);
    _setTokens(access_token, refresh_token);
    try { setUser(await users.me()); }
    catch { setUser({ id: "", email, full_name: name ?? null, is_active: true, is_verified: false }); }
  };

  const loginAsGuest = async () => {
    const { access_token, refresh_token } = await auth.guest();
    _setTokens(access_token, refresh_token);
    // Fetch the real guest user so the ID is correct for session isolation.
    try { setUser(await users.me()); }
    catch { setUser({ id: "", email: "guest", full_name: "Guest", is_active: true, is_verified: false }); }
  };

  const logout = () => {
    _clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, loginAsGuest, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
