'use client';

import { useAuth } from "@/app/context/AuthContext";
import { useRouter } from "next/navigation";
import { useState } from "react";
import AuthLayout from "../layout/AuthLayout";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();

  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [passwordVisible, setPasswordVisible] = useState(false);
  
  const togglePasswordVisibility = () => setPasswordVisible((prev) => !prev);


  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    const ok = await signup(username, email, password, name);
    if (ok) {
      router.push("/dashboard");
    }
  };

  return (
    <AuthLayout title="Sign up">
      <form onSubmit={handleSignup}>
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
          <input
            type="text"
            className="form-control"
            placeholder="なまえ"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>


        <div className="mb-3">
          <input
            type="email"
            className="form-control"
            placeholder="メールアドレス"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
          登録する
        </button>
      </form>
    </AuthLayout>
  );
}

