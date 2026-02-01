
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/app/context/AuthContext";
import Image from "next/image";

type User = {
  id: string;
  username: string;
  name: string;
  profile: {
    image: string | null;
    role: string;
  };
  point_balance: number;
};

type Item = {
  id: number;
  name: string;
  price: number;
  image_url: string;
};

type ProductItem = {
  title: string;
  image: string;
  price: number | null;
  url: string;
};

export default function Dashboard() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";


  const [items, setItems] = useState<Item[]>([]);

  const [keyword, setKeyword] = useState("");
  const [amazonProducts, setAmazonProducts] = useState<ProductItem[]>([]);
  const [isSearch, setIsSearch] = useState(false);
  const [page, setPage] = useState(1);
  const totalPages = 5;


  const [amazonLoading, setAmazonLoading] = useState(false);

  const { user, isAuthenticated, logout } = useAuth();

  useEffect(() => {
    async function fetchItems() {
      try {
        const res = await fetch(`${apiBaseUrl}/api/items/`, {
          credentials: "include",
        });
        if (res.ok) {
          setItems(await res.json());
        }
      } catch {
        console.error("Item fetch error");
      }
    }
    fetchItems();
  }, []);

  const handleAmazonSearch = async (newPage = 1) => {
    if (!keyword.trim()) return;

    setPage(newPage);
    setIsSearch(true);
    setAmazonLoading(true);

    try {
      const res = await fetch(
        `/api/amazon?keyword=${encodeURIComponent(keyword)}&page=${newPage}`
      );

      if (!res.ok) {
        const text = await res.text();
        console.error("APIエラー:", res.status, text);
        alert(`Amazon検索に失敗しました (${res.status})`);
        return;
      }

      const data: { items?: ProductItem[] } = await res.json();

      if (Array.isArray(data.items)) {
        setAmazonProducts(data.items);
      } else {
        setAmazonProducts([]);
      }

      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error("通信エラー:", err);
      alert("通信エラーが発生しました");
    } finally {
      setAmazonLoading(false);
    }
  };

  const renderPagination = () => {
    if (!isSearch || amazonProducts.length === 0) return null;

    return (
      <div className="flex justify-center items-center gap-2 mt-6">
        <button
          onClick={() => handleAmazonSearch(page - 1)}
          disabled={page === 1}
          className="px-3 py-1 bg-gray-300 rounded disabled:opacity-50"
        >
          前へ
        </button>

        {[...Array(totalPages)].map((_, i) => {
          const pageNum = i + 1;
          return (
            <button
              key={pageNum}
              onClick={() => handleAmazonSearch(pageNum)}
              className={`px-3 py-1 rounded ${page === pageNum ? "bg-blue-600 text-white" : "bg-gray-200"
                }`}
            >
              {pageNum}
            </button>
          );
        })}

        <button
          onClick={() => handleAmazonSearch(page + 1)}
          disabled={page === totalPages}
          className="px-3 py-1 bg-gray-300 rounded disabled:opacity-50"
        >
          次へ
        </button>
      </div>
    );
  };

  if (isAuthenticated === null) {
    return <p className="text-center text-gray-600 mt-20">読み込み中...</p>;
  }

  if (!user) {
    return <p className="text-center text-gray-600 mt-20">
      ログイン情報を取得できませんでした。
    </p>;
  }

  const getImageUrl = (path: string | null) => {
    if (!path) return "/default.png";
    if (path.startsWith("http")) return path;
    return `${apiBaseUrl}${path}`;
  };


  return (
    <>
      <main className="bg-gray-50 min-h-screen py-8 px-4">
        <section className="profiles flex justify-center mb-10">
          <div className="profile bg-white rounded-2xl shadow p-6 text-center w-full max-w-md">
            {user ? (
              <>
                <div className="flex justify-center mb-3">
                  <Image
                    src={user.profile?.image || "/default.png"}
                    alt="profile"
                    width={250}
                    height={250}
                    className="w-24 h-24 rounded-full object-cover border"
                    unoptimized
                  />
                </div>

                <p className="text-lg font-semibold">{user.name}</p>

                <div className="mt-2">
                  {user.point_balance != null ? (
                    <p>
                      <span className="text-2xl font-bold">
                        {user.point_balance.toLocaleString()}
                      </span>{" "}
                      ダン
                    </p>
                  ) : (
                    <p className="text-sm text-gray-500">
                      ポイントデータがありません。
                    </p>
                  )}

                  <button onClick={logout} className="mt-4 underline text-sm">
                    ログアウト
                  </button>
                </div>
              </>
            ) : (
              <p>ログイン情報を取得できませんでした。</p>
            )}
          </div>
        </section>

        <section className="max-w-6xl mx-auto">
          <div className="flex flex-col sm:flex-row justify-between items-center mb-4">
            <h2 className="text-2xl font-bold tracking-tight text-gray-900">ダンカタログ</h2>

            {/* <div className="flex gap-2">
              <input
                name="keyword"
                id="keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Amazonで検索"
                className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
              />
              <button
                onClick={() => handleAmazonSearch(1)}
                className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm"
              >
                検索
              </button>
            </div> */}
          </div>

          {amazonLoading && (
            <p className="text-center text-gray-500 mt-4">読み込み中...</p>
          )}

          {isSearch && !amazonLoading && (
            <>
              <h2 className="mb-4 text-lg">🔍 Amazon検索結果</h2>

              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
                {amazonProducts.map((p, idx) => (
                  <a
                    key={idx}
                    href={p.url}
                    target="_blank"
                    className="block bg-white shadow rounded-xl p-3 hover:shadow-md transition text-center"
                  >
                    <img
                      src={p.image}
                      alt={p.title}
                      className="mx-auto w-3/4 h-40 object-contain mb-2"
                    />
                    <p className="text-sm line-clamp-2">{p.title}</p>
                    <p className="text-lg font-semibold mt-1">
                      {p.price ? `¥${p.price}` : "価格不明"}
                    </p>
                  </a>
                ))}
              </div>

              <pre className="mt-4 bg-yellow-100 p-4 text-xs rounded text-yellow-900">
                {JSON.stringify(amazonProducts, null, 2)}
              </pre>

              {renderPagination()}
            </>
          )}

          {!isSearch && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-3 gap-6">
              {items.map((item) => (
                <div
                  key={item.id}
                  className="rounded-xl object-cover group-hover:opacity-75 bg-white shadow p-3 hover:shadow-md transition"
                >
                  <Link href={`/items/${item.id}`} className="block text-center [text-decoration:none]">
                    <img
                      src={getImageUrl(item.image_url)}
                      alt={item.name}
                      className="mx-auto w-3/4 h-40 object-contain mb-2"
                    />
                    <p className="text-2xl mb-1 line-clamp-2 mt-1 font-semibold text-gray-800">
                      {item.name}
                    </p>
                    <p className="text-lg font-semibold text-gray-700">{item.price} ダン</p>
                  </Link>


                </div>
              ))}
            </div>
          )}
        </section>
      </main>

    </>
  );
}
