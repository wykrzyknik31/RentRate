"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function Register() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    username: "",
    terms_accepted: false,
  });
  const [errors, setErrors] = useState({
    email: "",
    password: "",
    terms: "",
    general: "",
  });
  const [loading, setLoading] = useState(false);

  const validateEmail = (email: string) => {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
  };

  const validatePassword = (password: string) => {
    const errors: string[] = [];
    if (password.length < 8) {
      errors.push("at least 8 characters");
    }
    if (!/[A-Z]/.test(password)) {
      errors.push("one uppercase letter");
    }
    if (!/\d/.test(password)) {
      errors.push("one number");
    }
    return errors;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === "checkbox" ? checked : value,
    });

    // Clear errors on change
    if (name === "email") {
      setErrors({ ...errors, email: "", general: "" });
    } else if (name === "password") {
      setErrors({ ...errors, password: "", general: "" });
    } else if (name === "terms_accepted") {
      setErrors({ ...errors, terms: "", general: "" });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Validate email
    if (!formData.email) {
      setErrors({ ...errors, email: "Email is required", general: "" });
      setLoading(false);
      return;
    }
    if (!validateEmail(formData.email)) {
      setErrors({ ...errors, email: "Invalid email format", general: "" });
      setLoading(false);
      return;
    }

    // Validate password
    if (!formData.password) {
      setErrors({ ...errors, password: "Password is required", general: "" });
      setLoading(false);
      return;
    }
    const passwordErrors = validatePassword(formData.password);
    if (passwordErrors.length > 0) {
      setErrors({
        ...errors,
        password: `Password must contain ${passwordErrors.join(", ")}`,
        general: "",
      });
      setLoading(false);
      return;
    }

    // Validate terms
    if (!formData.terms_accepted) {
      setErrors({
        ...errors,
        terms: "You must accept the terms and conditions",
        general: "",
      });
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:5000/api/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        // Redirect to homepage on success
        router.push("/");
      } else {
        setErrors({
          email: "",
          password: "",
          terms: "",
          general: data.error || "Registration failed. Please try again.",
        });
      }
    } catch (error) {
      setErrors({
        email: "",
        password: "",
        terms: "",
        general: "Network error. Please check if the backend is running.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <Link href="/">
            <h1 className="text-3xl font-bold cursor-pointer">RentRate</h1>
          </Link>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-md">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            Create Account
          </h2>

          <form onSubmit={handleSubmit}>
            {errors.general && (
              <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                {errors.general}
              </div>
            )}

            <div className="mb-4">
              <label
                htmlFor="email"
                className="block text-gray-700 font-medium mb-2"
              >
                Email *
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                  errors.email
                    ? "border-red-500 focus:ring-red-500"
                    : "border-gray-300 focus:ring-blue-500"
                }`}
                placeholder="your@email.com"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            <div className="mb-4">
              <label
                htmlFor="username"
                className="block text-gray-700 font-medium mb-2"
              >
                Username (Optional)
              </label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="username"
              />
            </div>

            <div className="mb-4">
              <label
                htmlFor="password"
                className="block text-gray-700 font-medium mb-2"
              >
                Password *
              </label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                  errors.password
                    ? "border-red-500 focus:ring-red-500"
                    : "border-gray-300 focus:ring-blue-500"
                }`}
                placeholder="••••••••"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
              <p className="mt-1 text-sm text-gray-600">
                Must be at least 8 characters with 1 uppercase letter and 1
                number
              </p>
            </div>

            <div className="mb-6">
              <label className="flex items-start">
                <input
                  type="checkbox"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  className={`mt-1 mr-2 ${
                    errors.terms ? "border-red-500" : ""
                  }`}
                />
                <span className="text-gray-700">
                  I accept the terms and conditions *
                </span>
              </label>
              {errors.terms && (
                <p className="mt-1 text-sm text-red-600">{errors.terms}</p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {loading ? "Creating Account..." : "Create Account"}
            </button>
          </form>

          <p className="mt-4 text-center text-gray-600">
            Already have an account?{" "}
            <Link href="/login" className="text-blue-600 hover:underline">
              Log in
            </Link>
          </p>
        </div>
      </main>
    </div>
  );
}
