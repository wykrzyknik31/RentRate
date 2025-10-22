"use client";

import { useTranslation } from "react-i18next";

const languages = [
  { code: "pl", name: "Polski", flag: "PL" },
  { code: "en", name: "English", flag: "EN" },
  { code: "ru", name: "Русский", flag: "RU" },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const changeLanguage = (locale: string) => {
    i18n.changeLanguage(locale);
  };

  return (
    <div className="flex items-center gap-2">
      {languages.map((lang) => (
        <button
          key={lang.code}
          onClick={() => changeLanguage(lang.code)}
          className={`px-3 py-1 rounded-lg transition-colors ${
            i18n.language === lang.code
              ? "bg-blue-700 text-white"
              : "bg-blue-500 text-white hover:bg-blue-600"
          }`}
          title={lang.name}
        >
          <span className="font-semibold text-sm">{lang.flag}</span>
        </button>
      ))}
    </div>
  );
}
