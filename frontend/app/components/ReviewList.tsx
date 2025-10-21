"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

interface Property {
  id: number;
  address: string;
  property_type: string;
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
  created_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export default function ReviewList() {
  const { t } = useTranslation("common");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/api/reviews`);
      if (!response.ok) {
        throw new Error("Failed to fetch reviews");
      }
      const data = await response.json();
      setReviews(data);
    } catch (err) {
      // Provide a more helpful error message when backend is not available
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError(
          t("reviewList.backendError", { url: API_URL })
        );
      } else {
        setError(err instanceof Error ? err.message : "An error occurred");
      }
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`w-5 h-5 ${
              star <= rating ? "text-yellow-400" : "text-gray-300"
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
        {t("reviewList.error", { message: error })}
      </div>
    );
  }

  if (reviews.length === 0) {
    return (
      <div className="bg-gray-100 border border-gray-200 rounded-lg p-8 text-center">
        <p className="text-gray-600 text-lg">
          {t("reviewList.noReviews")}
        </p>
      </div>
    );
  }

  return (
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
              <span className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded mt-2">
                {review.property.property_type}
              </span>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500 mb-1">{t("reviewList.propertyRating")}</p>
              {renderStars(review.rating)}
            </div>
          </div>

          <div className="mb-4">
            <p className="text-gray-700 leading-relaxed">
              {review.review_text || t("reviewList.noComment")}
            </p>
          </div>

          {review.landlord_name && (
            <div className="border-t pt-4 mt-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600">{t("reviewList.landlord")}</p>
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

          <div className="mt-4 pt-4 border-t flex justify-between items-center text-sm text-gray-500">
            <span>{t("reviewList.reviewedBy", { name: review.reviewer_name })}</span>
            <span>{new Date(review.created_at).toLocaleDateString()}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
