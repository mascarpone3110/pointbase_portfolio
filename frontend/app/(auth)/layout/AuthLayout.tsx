'use client';

import Link from "next/link";
import React from "react";

export default function AuthLayout({
  children,
  title,
}: {
  children: React.ReactNode;
  title: string;
}) {
  return (
    <section className="auth-layout" style={{ minHeight: "100vh" }}>
      <div className="d-flex align-items-center justify-content-center vh-100">
        <div
          className="card shadow-sm p-4"
          style={{
            width: "380px",
            borderRadius: "12px",
            backgroundColor: "#fff",
          }}
        >
          <h2
            className="text-center fw-bold mb-4"
            style={{ letterSpacing: "0.5px" }}
          >
            {title}
          </h2>

          {children}

          <div className="text-center mt-3">
            {title === "Login" ? (
              <p>
                アカウントをお持ちでない方は{" "}
                <Link href="/signup" className="text-decoration-none">
                  登録はこちら
                </Link>
              </p>
            ) : (
              <p>
                すでに登録済みの方は{" "}
                <Link href="/login" className="text-decoration-none">
                  ログインへ
                </Link>
              </p>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
