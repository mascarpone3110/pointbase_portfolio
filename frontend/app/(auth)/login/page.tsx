'use client';

import { useEffect, useState } from "react";
import AuthLayout from "../layout/AuthLayout";
import { useAuth } from "@/app/context/AuthContext";
import { useApiBaseUrl } from "@/app/hooks/useApiBaseUrl";



export default function LoginPage() {

  const { login } = useAuth();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  const togglePasswordVisibility = () => setPasswordVisible((prev) => !prev);

  const { apiBaseUrl, loading } = useApiBaseUrl();


  // 初回ロード時にCookieを削除（古いJWTをクリア）
  useEffect(() => {
    if (loading) return;
    if (!apiBaseUrl) return;

    const clearTokens = async () => {
      try {
        await fetch(`${apiBaseUrl}/api/clear-tokens/`, {
          method: "POST",
          credentials: "include",
        });
      } catch (err) {
        console.error("Token clear failed:", err);
      }
    };

    clearTokens();
  }, [apiBaseUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(username, password);
  };

  return (
    <AuthLayout title="Login">
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <input
            type="text"
            className="form-control"
            placeholder="ユーザー名"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <div className="input-group">
            <input
              type={passwordVisible ? "text" : "password"}
              className="form-control"
              placeholder="パスワード"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={togglePasswordVisibility}
            >
              <i
                className={`bi ${passwordVisible ? "bi-eye-slash" : "bi-eye"}`}
              ></i>
            </button>
          </div>
        </div>

        <button
          type="submit"
          className="btn w-100"
          style={{
            backgroundColor: "#000",
            color: "#fff",
            borderColor: "#000",
          }}
        >
          ログイン
        </button>
      </form>
    </AuthLayout>
  );
}
