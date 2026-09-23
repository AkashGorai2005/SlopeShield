import { createContext, createElement, useContext, useEffect, useMemo, useState } from "react";

const STORAGE_KEY = "SLOPESHIELDUser";
const AUTH_KEY = "SLOPESHIELDAuthenticated";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (typeof window === "undefined") return null;
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    if (typeof window === "undefined") return false;
    return window.localStorage.getItem(AUTH_KEY) === "true";
  });

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (user) {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
      window.localStorage.setItem(AUTH_KEY, "true");
      setIsAuthenticated(true);
    } else {
      window.localStorage.removeItem(STORAGE_KEY);
      window.localStorage.setItem(AUTH_KEY, "false");
      setIsAuthenticated(false);
    }
  }, [user]);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated,
      signIn: (nextUser) => {
        setUser(nextUser);
      },
      signOut: () => {
        setUser(null);
      },
    }),
    [isAuthenticated, user],
  );

  return createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within <AuthProvider>");
  }
  return context;
}

export function getStoredUser() {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function signOutDemo() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem(STORAGE_KEY);
  window.localStorage.setItem(AUTH_KEY, "false");
}
