"use client";

import Link from "next/link";
import ReviewList from "./components/ReviewList";
import Navbar from "./components/Navbar";
import { useTranslation } from "react-i18next";

export default function Home() {
  const { t } = useTranslation("common");

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">{t("home.recentReviews")}</h2>
          <Link
            href="/add-review"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {t("home.addReview")}
          </Link>
        </div>

        <ReviewList />
      </main>

      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>{t("home.footer")}</p>
        </div>
      </footer>
    </div>
  );
}
