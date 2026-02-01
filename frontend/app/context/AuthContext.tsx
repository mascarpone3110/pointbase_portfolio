"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
} from "react";
import { useRouter, usePathname } from "next/navigation";
import { getCookie } from "@/lib/utils/getCookie";

/* ======================================
   UserType（/api/me/ 準拠）
====================================== */
export type UserType = {
  id: string;
  username: string;
  name: string;
  point_balance: number;
  profile: {
    image: string | null;
    role: "student" | "teacher" | "admin";
    is_totp_verified: boolean;
  };
};

/* ======================================
   AuthContextType
====================================== */
type AuthContextType = {
  isAuthenticated: boolean | null;
  username: string | null;
  user: UserType | null;
  role: "student" | "teacher" | "admin" | null;

  login: (username: string, password: string) => Promise<void>;
  signup: (
    username: string,
    email: string,
    password: string,
    name: string
  ) => Promise<boolean>;
  logout: () => Promise<void>;
};

/* ======================================
   🔵 Context
====================================== */
const AuthContext = createContext<AuthContextType>({
  isAuthenticated: null,
  username: null,
  user: null,
  role: null,
  login: async () => { },
  signup: async () => false,
  logout: async () => { },
});

export const useAuth = () => useContext(AuthContext);

/* ======================================
   🔵 AuthProvider
====================================== */
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();
  const pathname = usePathname();

  const PUBLIC_ROUTES = new Set(["/login", "/signup"]);

  const [apiBaseUrl, setApiBaseUrl] = useState<string | null>(null);

  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [username, setUsername] = useState<string | null>(null);
  const [user, setUser] = useState<UserType | null>(null);
  const [role, setRole] =
    useState<"student" | "teacher" | "admin" | null>(null);

  /* ======================================
     🔵 Cookie削除
  ====================================== */
  const clearCookies = () => {
    document.cookie = "access_token=; Max-Age=0; path=/;";
    document.cookie = "refresh_token=; Max-Age=0; path=/;";
  };

  /* ======================================
     runtime API URL 取得（1回のみ）
  ====================================== */
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch("/api/config", { cache: "no-store" });
        const data = await res.json();
        setApiBaseUrl(data.apiBaseUrl);
      } catch (e) {
        console.error("Failed to load api config", e);
      }
    })();
  }, []);

  /* ======================================
     API fetch ラッパー
  ====================================== */
  const apiFetch = useCallback(
    (path: string, options?: RequestInit) => {
      if (!apiBaseUrl) throw new Error("API not ready");
      return fetch(`${apiBaseUrl}${path}`, {
        credentials: "include",
        ...options,
      });
    },
    [apiBaseUrl]
  );

  /* ======================================
     /api/me/
  ====================================== */
  const loadUser = useCallback(async () => {
    if (!apiBaseUrl) return null;

    try {
      await apiFetch("/api/csrf/");

      const res = await apiFetch("/api/me/");
      if (res.status === 401) {
        setIsAuthenticated(false);
        setUsername(null);
        setUser(null);
        setRole(null);
        return null;
      }

      if (!res.ok) throw new Error("Failed to fetch /api/me/");

      const data: UserType = await res.json();

      setIsAuthenticated(true);
      setUsername(data.username);
      setUser(data);
      setRole(data.profile.role);

      return data;
    } catch (e) {
      console.error("loadUser error:", e);
      setIsAuthenticated(false);
      setUsername(null);
      setUser(null);
      setRole(null);
      return null;
    }
  }, [apiBaseUrl, apiFetch]);

  /* ======================================
     初回アクセス
  ====================================== */
  useEffect(() => {
    if (!apiBaseUrl) return;

    (async () => {
      const me = await loadUser();
      if (!me && !PUBLIC_ROUTES.has(pathname)) {
        router.push("/login");
      }
    })();
  }, [apiBaseUrl, pathname, loadUser, router]);

  /* ======================================
     login
  ====================================== */
  const login = async (username: string, password: string) => {
    try {
      await apiFetch("/api/csrf/");
      const csrfToken = getCookie("csrftoken");

      const res = await apiFetch("/api/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({ username, password }),
      });

      if (!res.ok) {
        alert("ログイン失敗");
        return;
      }

      const me = await loadUser();
      if (!me) {
        alert("認証情報取得失敗");
        return;
      }

      router.push("/dashboard");
    } catch (e) {
      console.error(e);
      alert("通信エラー");
    }
  };

  /* ======================================
     signup
  ====================================== */
  const signup = async (
    username: string,
    email: string,
    password: string,
    name: string
  ) => {
    try {
      clearCookies();
      await apiFetch("/api/csrf/");
      const csrfToken = getCookie("csrftoken");

      const res = await apiFetch("/api/signup/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken || "",
        },
        body: JSON.stringify({ username, email, password, name }),
      });

      if (res.status !== 201) {
        const e = await res.json();
        alert("登録失敗: " + (e.error ?? ""));
        return false;
      }

      await login(username, password);
      return true;
    } catch (e) {
      console.error(e);
      alert("通信エラー");
      return false;
    }
  };

  /* ======================================
     logout
  ====================================== */
  const logout = async () => {
    try {
      await apiFetch("/api/logout/", { method: "POST" });
    } catch (e) {
      console.error(e);
    } finally {
      clearCookies();
      setIsAuthenticated(false);
      setUsername(null);
      setUser(null);
      setRole(null);
      router.push("/login");
    }
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        username,
        user,
        role,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
