"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import LanguageSwitcher from "./LanguageSwitcher";

export default function Navbar() {
  const router = useRouter();
  const { t } = useTranslation("common");
  const [user, setUser] = useState<{ username?: string; email: string } | null>(
    null
  );
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/profile", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();
        setUser(data);
      } else {
        setUser(null);
      }
    } catch (error) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch("http://localhost:5000/api/logout", {
        method: "POST",
        credentials: "include",
      });
      setUser(null);
      router.push("/");
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  return (
    <header className="bg-blue-600 text-white py-6 shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center">
          <div>
            <Link href="/">
              <h1 className="text-3xl font-bold cursor-pointer">{t("nav.title")}</h1>
            </Link>
            <p className="text-blue-100 mt-2">
              {t("nav.subtitle")}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
            {loading ? (
              <div className="text-blue-100">{t("nav.loading")}</div>
            ) : user ? (
              <>
                <Link
                  href="/my-reviews"
                  className="text-white hover:text-blue-100 transition-colors"
                >
                  {t("myReviews.title")}
                </Link>
                <span className="text-white">
                  {t("nav.welcome", { name: user.username || user.email })}
                </span>
                <button
                  onClick={handleLogout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-lg transition-colors"
                >
                  {t("nav.logout")}
                </button>
              </>
            ) : (
              <>
                <Link
                  href="/login"
                  className="text-white hover:text-blue-100 transition-colors"
                >
                  {t("nav.login")}
                </Link>
                <Link
                  href="/register"
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-lg transition-colors"
                >
                  {t("nav.register")}
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
