"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

export default function AddReview() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    address: "",
    property_type: "apartment",
    reviewer_name: "",
    rating: 3,
    review_text: "",
    landlord_name: "",
    landlord_rating: 3,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const reviewData = {
        ...formData,
        landlord_name: formData.landlord_name || undefined,
        landlord_rating: formData.landlord_name
          ? formData.landlord_rating
          : undefined,
      };

      const response = await fetch(`${API_URL}/api/reviews`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(reviewData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Failed to submit review");
      }

      // Redirect to home page after successful submission
      router.push("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "number" || name.includes("rating") ? parseInt(value) : value,
    }));
  };

  const renderStarSelector = (fieldName: "rating" | "landlord_rating") => {
    const value = formData[fieldName];
    return (
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() =>
              setFormData((prev) => ({ ...prev, [fieldName]: star }))
            }
            className="focus:outline-none"
          >
            <svg
              className={`w-8 h-8 ${
                star <= value ? "text-yellow-400" : "text-gray-300"
              } hover:text-yellow-300 transition-colors`}
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">RentRate</h1>
          <p className="text-blue-100 mt-2">Add a new review</p>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-2xl">
        <div className="mb-6">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Reviews
          </Link>
        </div>

        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Submit Your Review
          </h2>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 text-red-700">
              Error: {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Property Information */}
            <div>
              <label
                htmlFor="address"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Property Address *
              </label>
              <input
                type="text"
                id="address"
                name="address"
                required
                value={formData.address}
                onChange={handleChange}
                placeholder="e.g., 123 Main St, Apt 4B"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label
                htmlFor="property_type"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Property Type *
              </label>
              <select
                id="property_type"
                name="property_type"
                required
                value={formData.property_type}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="room">Room</option>
                <option value="apartment">Apartment</option>
                <option value="house">House</option>
              </select>
            </div>

            {/* Reviewer Information */}
            <div>
              <label
                htmlFor="reviewer_name"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Your Name *
              </label>
              <input
                type="text"
                id="reviewer_name"
                name="reviewer_name"
                required
                value={formData.reviewer_name}
                onChange={handleChange}
                placeholder="John Doe"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Property Rating */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Property Rating *
              </label>
              {renderStarSelector("rating")}
            </div>

            {/* Review Text */}
            <div>
              <label
                htmlFor="review_text"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Your Review *
              </label>
              <textarea
                id="review_text"
                name="review_text"
                required
                value={formData.review_text}
                onChange={handleChange}
                rows={5}
                placeholder="Share your experience with this property..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Landlord Information (Optional) */}
            <div className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Landlord Information (Optional)
              </h3>

              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="landlord_name"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Landlord Name
                  </label>
                  <input
                    type="text"
                    id="landlord_name"
                    name="landlord_name"
                    value={formData.landlord_name}
                    onChange={handleChange}
                    placeholder="Jane Smith"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {formData.landlord_name && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Landlord Rating
                    </label>
                    {renderStarSelector("landlord_rating")}
                  </div>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {loading ? "Submitting..." : "Submit Review"}
              </button>
              <Link
                href="/"
                className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700"
              >
                Cancel
              </Link>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}
