"use client";

import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

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

interface TranslationState {
  [reviewId: number]: {
    translatedText: string;
    sourceLang: string;
    isTranslated: boolean;
    isTranslating: boolean;
    error: string | null;
  };
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

// Language code mapping for display
const languageNames: { [key: string]: string } = {
  en: "English",
  pl: "Polish",
  ru: "Russian",
  es: "Spanish",
  fr: "French",
  de: "German",
  it: "Italian",
  pt: "Portuguese",
  zh: "Chinese",
  ja: "Japanese",
  ko: "Korean",
};

export default function ReviewList() {
  const { t, i18n } = useTranslation("common");
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [translations, setTranslations] = useState<TranslationState>({});
  const [detectedLanguages, setDetectedLanguages] = useState<{ [reviewId: number]: string }>({});
  
  // Filter and sort states
  const [cities, setCities] = useState<string[]>([]);
  const [selectedCity, setSelectedCity] = useState<string>("");
  const [selectedRating, setSelectedRating] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("recent");

  useEffect(() => {
    fetchCities();
  }, []);

  useEffect(() => {
    fetchReviews();
  }, [selectedCity, selectedRating, sortBy]);

  useEffect(() => {
    // Detect languages for all reviews when they load
    reviews.forEach((review) => {
      if (review.review_text && !detectedLanguages[review.id]) {
        detectLanguage(review.id, review.review_text);
      }
    });
  }, [reviews]);

  const fetchCities = async () => {
    try {
      const response = await fetch(`${API_URL}/api/cities`);
      if (response.ok) {
        const data = await response.json();
        setCities(data);
      }
    } catch (err) {
      console.error("Failed to fetch cities:", err);
    }
  };

  const fetchReviews = async () => {
    try {
      setLoading(true);
      
      // Build query parameters
      const params = new URLSearchParams();
      if (selectedCity) params.append("city", selectedCity);
      if (selectedRating) params.append("rating", selectedRating);
      if (sortBy) params.append("sort", sortBy);
      
      const queryString = params.toString();
      const url = `${API_URL}/api/reviews${queryString ? `?${queryString}` : ""}`;
      
      const response = await fetch(url);
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

  const detectLanguage = async (reviewId: number, text: string) => {
    try {
      const response = await fetch(`${API_URL}/api/detect-language`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      });

      if (response.ok) {
        const data = await response.json();
        setDetectedLanguages((prev) => ({
          ...prev,
          [reviewId]: data.detected_language,
        }));
      }
    } catch (err) {
      // Silently fail language detection
      console.error("Language detection failed:", err);
    }
  };

  const translateReview = async (reviewId: number, text: string) => {
    const currentLang = i18n.language;

    setTranslations((prev) => ({
      ...prev,
      [reviewId]: {
        ...prev[reviewId],
        isTranslating: true,
        error: null,
      },
    }));

    try {
      const response = await fetch(`${API_URL}/api/translate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text,
          target_lang: currentLang,
        }),
      });

      if (!response.ok) {
        throw new Error("Translation failed");
      }

      const data = await response.json();

      setTranslations((prev) => ({
        ...prev,
        [reviewId]: {
          translatedText: data.translated_text,
          sourceLang: data.source_lang,
          isTranslated: true,
          isTranslating: false,
          error: null,
        },
      }));
    } catch (err) {
      setTranslations((prev) => ({
        ...prev,
        [reviewId]: {
          ...prev[reviewId],
          isTranslating: false,
          error: t("reviewList.translationError"),
        },
      }));
    }
  };

  const toggleTranslation = (reviewId: number) => {
    setTranslations((prev) => ({
      ...prev,
      [reviewId]: {
        ...prev[reviewId],
        isTranslated: !prev[reviewId]?.isTranslated,
      },
    }));
  };

  const shouldShowTranslateButton = (reviewId: number) => {
    const detectedLang = detectedLanguages[reviewId];
    const currentLang = i18n.language;
    
    // Show translate button if language is detected and different from UI language
    return detectedLang && detectedLang !== currentLang;
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
      {/* Filter and Sort Controls */}
      <div className="bg-white rounded-lg shadow-md p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* City Filter */}
          <div>
            <label htmlFor="city-filter" className="block text-sm font-medium text-gray-700 mb-2">
              {t("reviewList.filterByCity")}
            </label>
            <select
              id="city-filter"
              value={selectedCity}
              onChange={(e) => setSelectedCity(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t("reviewList.allCities")}</option>
              {cities.map((city) => (
                <option key={city} value={city}>
                  {city}
                </option>
              ))}
            </select>
          </div>

          {/* Rating Filter */}
          <div>
            <label htmlFor="rating-filter" className="block text-sm font-medium text-gray-700 mb-2">
              {t("reviewList.filterByRating")}
            </label>
            <select
              id="rating-filter"
              value={selectedRating}
              onChange={(e) => setSelectedRating(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">{t("reviewList.allRatings")}</option>
              <option value="5">{t("reviewList.rating5Plus")}</option>
              <option value="4">{t("reviewList.rating4Plus")}</option>
              <option value="3">{t("reviewList.rating3Plus")}</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <label htmlFor="sort-by" className="block text-sm font-medium text-gray-700 mb-2">
              {t("reviewList.sortBy")}
            </label>
            <select
              id="sort-by"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="recent">{t("reviewList.sortRecent")}</option>
              <option value="rating_desc">{t("reviewList.sortHighestRating")}</option>
              <option value="rating_asc">{t("reviewList.sortLowestRating")}</option>
            </select>
          </div>
        </div>

        {/* Clear Filters Button */}
        {(selectedCity || selectedRating || sortBy !== "recent") && (
          <div className="mt-4">
            <button
              onClick={() => {
                setSelectedCity("");
                setSelectedRating("");
                setSortBy("recent");
              }}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium"
            >
              {t("reviewList.clearFilters")}
            </button>
          </div>
        )}
      </div>

      {/* Reviews */}
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
            <div className="text-right">
              <p className="text-sm text-gray-500 mb-1">{t("reviewList.propertyRating")}</p>
              {renderStars(review.rating)}
            </div>
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
                    onClick={() => window.open(`${API_URL}${photo.url}`, '_blank')}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="mb-4">
            <p className="text-gray-700 leading-relaxed">
              {translations[review.id]?.isTranslated
                ? translations[review.id].translatedText
                : review.review_text || t("reviewList.noComment")}
            </p>
            
            {review.review_text && shouldShowTranslateButton(review.id) && (
              <div className="mt-3 flex items-center gap-2">
                {!translations[review.id]?.translatedText ? (
                  <button
                    onClick={() => translateReview(review.id, review.review_text)}
                    disabled={translations[review.id]?.isTranslating}
                    className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {translations[review.id]?.isTranslating ? (
                      <>
                        <svg
                          className="animate-spin -ml-0.5 mr-2 h-4 w-4 text-blue-600"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          />
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          />
                        </svg>
                        {t("reviewList.translating")}
                      </>
                    ) : (
                      <>
                        <svg
                          className="-ml-0.5 mr-2 h-4 w-4"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                          />
                        </svg>
                        {t("reviewList.translate")}
                      </>
                    )}
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => toggleTranslation(review.id)}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
                    >
                      {translations[review.id]?.isTranslated ? (
                        <>
                          <svg
                            className="-ml-0.5 mr-2 h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                            />
                          </svg>
                          {t("reviewList.showOriginal")}
                        </>
                      ) : (
                        <>
                          <svg
                            className="-ml-0.5 mr-2 h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129"
                            />
                          </svg>
                          {t("reviewList.translate")}
                        </>
                      )}
                    </button>
                    {translations[review.id]?.isTranslated && (
                      <span className="text-xs text-gray-500 italic">
                        {t("reviewList.translated", {
                          language: languageNames[translations[review.id].sourceLang] || translations[review.id].sourceLang,
                        })}
                      </span>
                    )}
                  </>
                )}
                {translations[review.id]?.error && (
                  <span className="text-xs text-red-600">
                    {translations[review.id].error}
                  </span>
                )}
              </div>
            )}
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
