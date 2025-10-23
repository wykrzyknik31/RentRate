"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTranslation } from "react-i18next";
import "../i18n";
import Navbar from "../components/Navbar";

interface Property {
  id: number;
  address: string;
  city?: string;
  property_type: string;
  created_at: string;
}

interface Photo {
  id: number;
  review_id: number;
  filename: string;
  url: string;
  created_at: string;
}

interface Review {
  id: number;
  property_id: number;
  property: Property;
  reviewer_name: string;
  rating: number;
  review_text: string;
  landlord_name: string | null;
  landlord_rating: number | null;
  photos: Photo[];
  created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export default function MyReviews() {
  const router = useRouter();
  const { t } = useTranslation("common");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingReview, setEditingReview] = useState<Review | null>(null);
  const [editFormData, setEditFormData] = useState({
    rating: 5,
    review_text: "",
    landlord_name: "",
    landlord_rating: 0,
    city: "",
  });
  const [editError, setEditError] = useState<string | null>(null);
  const [editLoading, setEditLoading] = useState(false);

  useEffect(() => {
    fetchMyReviews();
  }, []);

  const fetchMyReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/my-reviews`, {
        credentials: "include",
      });

      if (response.status === 401) {
        // User not authenticated, redirect to login
        router.push("/login");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch reviews");
      }

      const data = await response.json();
      setReviews(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (reviewId: number) => {
    if (!confirm(t("myReviews.confirmDelete"))) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/reviews/${reviewId}`, {
        method: "DELETE",
        credentials: "include",
      });

      if (!response.ok) {
        throw new Error("Failed to delete review");
      }

      // Remove from local state
      setReviews(reviews.filter((r) => r.id !== reviewId));
      alert(t("myReviews.deleteSuccess"));
    } catch (err) {
      alert(t("myReviews.deleteError"));
    }
  };

  const handleEdit = (review: Review) => {
    setEditingReview(review);
    setEditFormData({
      rating: review.rating,
      review_text: review.review_text || "",
      landlord_name: review.landlord_name || "",
      landlord_rating: review.landlord_rating || 0,
      city: review.property.city || "",
    });
    setEditError(null);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingReview) return;

    setEditLoading(true);
    setEditError(null);

    try {
      const response = await fetch(
        `${API_URL}/api/reviews/${editingReview.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            rating: editFormData.rating,
            review_text: editFormData.review_text,
            landlord_name: editFormData.landlord_name || null,
            landlord_rating: editFormData.landlord_rating || null,
            city: editFormData.city,
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Failed to update review");
      }

      const updatedReview = await response.json();

      // Update local state
      setReviews(
        reviews.map((r) => (r.id === updatedReview.id ? updatedReview : r))
      );

      setEditingReview(null);
      alert(t("myReviews.updateSuccess"));
    } catch (err) {
      setEditError(err instanceof Error ? err.message : t("myReviews.updateError"));
    } finally {
      setEditLoading(false);
    }
  };

  const renderStars = (rating: number, onRatingChange?: (rating: number) => void) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-5 h-5 ${
              star <= rating ? "text-yellow-400" : "text-gray-300"
            } ${onRatingChange ? "cursor-pointer" : ""}`}
            fill="currentColor"
            viewBox="0 0 20 20"
            onClick={() => onRatingChange && onRatingChange(star)}
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {t("myReviews.error", { message: error })}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">
            {t("myReviews.title")}
          </h2>
          <Link
            href="/add-review"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            {t("home.addReview")}
          </Link>
        </div>

        {reviews.length === 0 ? (
          <div className="bg-gray-100 border border-gray-200 rounded-lg p-8 text-center">
            <p className="text-gray-600 text-lg mb-4">
              {t("myReviews.noReviews")}
            </p>
            <Link
              href="/add-review"
              className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              {t("myReviews.addFirstReview")}
            </Link>
          </div>
        ) : (
          <div className="space-y-6">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800">
                      {review.property.address}
                    </h3>
                    {review.property.city && (
                      <p className="text-sm text-gray-600 mt-1">
                        {t("reviewList.city")}: {review.property.city}
                      </p>
                    )}
                    <span className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded mt-2">
                      {review.property.property_type}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(review)}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      {t("myReviews.edit")}
                    </button>
                    <button
                      onClick={() => handleDelete(review.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                    >
                      {t("myReviews.delete")}
                    </button>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-1">
                    {t("reviewList.propertyRating")}
                  </p>
                  {renderStars(review.rating)}
                </div>

                {/* Photos */}
                {review.photos && review.photos.length > 0 && (
                  <div className="mb-4">
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
                      {review.photos.map((photo) => (
                        <img
                          key={photo.id}
                          src={`${API_URL}${photo.url}`}
                          alt={photo.filename}
                          className="w-full h-24 object-cover rounded-lg border border-gray-200 hover:opacity-90 transition-opacity cursor-pointer"
                          onClick={() =>
                            window.open(`${API_URL}${photo.url}`, "_blank")
                          }
                        />
                      ))}
                    </div>
                  </div>
                )}

                <div className="mb-4">
                  <p className="text-gray-700 leading-relaxed">
                    {review.review_text || t("reviewList.noComment")}
                  </p>
                </div>

                {review.landlord_name && (
                  <div className="border-t pt-4 mt-4">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-600">
                          {t("reviewList.landlord")}
                        </p>
                        <p className="font-medium text-gray-800">
                          {review.landlord_name}
                        </p>
                      </div>
                      {review.landlord_rating && (
                        <div className="text-right">
                          <p className="text-sm text-gray-500 mb-1">
                            {t("reviewList.landlordRating")}
                          </p>
                          {renderStars(review.landlord_rating)}
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="mt-4 pt-4 border-t text-sm text-gray-500">
                  <span>
                    {t("myReviews.reviewedOn", {
                      date: new Date(review.created_at).toLocaleDateString(),
                    })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Edit Modal */}
      {editingReview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                {t("myReviews.editReview")}
              </h2>

              <form onSubmit={handleEditSubmit}>
                {editError && (
                  <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {editError}
                  </div>
                )}

                {/* Property Address (read-only) */}
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.propertyAddress")}
                  </label>
                  <input
                    type="text"
                    value={editingReview.property.address}
                    disabled
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-100"
                  />
                </div>

                {/* City */}
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.city")}
                  </label>
                  <input
                    type="text"
                    value={editFormData.city}
                    onChange={(e) =>
                      setEditFormData({ ...editFormData, city: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Rating */}
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.yourRating")} *
                  </label>
                  {renderStars(editFormData.rating, (rating) =>
                    setEditFormData({ ...editFormData, rating })
                  )}
                </div>

                {/* Review Text */}
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.yourReview")}
                  </label>
                  <textarea
                    value={editFormData.review_text}
                    onChange={(e) =>
                      setEditFormData({
                        ...editFormData,
                        review_text: e.target.value,
                      })
                    }
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Landlord Name */}
                <div className="mb-4">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.landlordName")}
                  </label>
                  <input
                    type="text"
                    value={editFormData.landlord_name}
                    onChange={(e) =>
                      setEditFormData({
                        ...editFormData,
                        landlord_name: e.target.value,
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Landlord Rating */}
                <div className="mb-6">
                  <label className="block text-gray-700 font-medium mb-2">
                    {t("myReviews.landlordRating")}
                  </label>
                  {renderStars(editFormData.landlord_rating || 0, (rating) =>
                    setEditFormData({ ...editFormData, landlord_rating: rating })
                  )}
                </div>

                {/* Buttons */}
                <div className="flex gap-4">
                  <button
                    type="submit"
                    disabled={editLoading}
                    className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
                  >
                    {editLoading
                      ? t("myReviews.updating")
                      : t("myReviews.updateReview")}
                  </button>
                  <button
                    type="button"
                    onClick={() => setEditingReview(null)}
                    className="flex-1 bg-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-400 transition-colors font-medium"
                  >
                    {t("myReviews.cancel")}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      <footer className="bg-gray-800 text-white py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>{t("home.footer")}</p>
        </div>
      </footer>
    </div>
  );
}
