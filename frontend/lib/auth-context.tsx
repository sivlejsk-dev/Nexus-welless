"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { auth, users, User } from "./api";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("nexus_access_token");
    if (token) {
      users.me()
        .then(setUser)
        .catch(() => localStorage.removeItem("nexus_access_token"))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    const { access_token, refresh_token } = await auth.login(email, password);
    localStorage.setItem("nexus_access_token", access_token);
    localStorage.setItem("nexus_refresh_token", refresh_token);
    try {
      const me = await users.me();
      setUser(me);
    } catch {
      // me() failed but login succeeded — set a minimal user so the redirect works
      setUser({ id: "", email, full_name: null, is_active: true, is_verified: false });
    }
  };

  const register = async (email: string, password: string, name?: string) => {
    const { access_token, refresh_token } = await auth.register(email, password, name);
    localStorage.setItem("nexus_access_token", access_token);
    localStorage.setItem("nexus_refresh_token", refresh_token);
    try {
      const me = await users.me();
      setUser(me);
    } catch {
      setUser({ id: "", email, full_name: name ?? null, is_active: true, is_verified: false });
    }
  };

  const logout = () => {
    localStorage.removeItem("nexus_access_token");
    localStorage.removeItem("nexus_refresh_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
