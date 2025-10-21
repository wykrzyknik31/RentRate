import i18n from "i18next";
import { initReactI18next } from "react-i18next";

// Import translation files
import plCommon from "../public/locales/pl/common.json";
import enCommon from "../public/locales/en/common.json";
import ruCommon from "../public/locales/ru/common.json";

// Get the language from localStorage or default to 'pl'
const getInitialLanguage = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('language') || 'pl';
  }
  return 'pl';
};

i18n
  .use(initReactI18next)
  .init({
    resources: {
      pl: {
        common: plCommon,
      },
      en: {
        common: enCommon,
      },
      ru: {
        common: ruCommon,
      },
    },
    lng: getInitialLanguage(),
    fallbackLng: "pl",
    defaultNS: "common",
    interpolation: {
      escapeValue: false,
    },
    react: {
      useSuspense: false,
    },
  });

// Save language changes to localStorage
i18n.on('languageChanged', (lng) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('language', lng);
  }
});

export default i18n;
