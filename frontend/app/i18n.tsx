'use client';

import { createInstance, type i18n as I18nInstance } from 'i18next';
import { initReactI18next, I18nextProvider } from 'react-i18next';
import { useEffect, useState, type ReactNode } from 'react';

// Import translation files
import plCommon from '../public/locales/pl/common.json';
import enCommon from '../public/locales/en/common.json';
import ruCommon from '../public/locales/ru/common.json';

const resources = {
  pl: {
    common: plCommon,
  },
  en: {
    common: enCommon,
  },
  ru: {
    common: ruCommon,
  },
};

// Create a default instance for SSR/initial render
function createI18nInstance(initialLng: string = 'pl'): I18nInstance {
  const i18n = createInstance();
  
  i18n
    .use(initReactI18next)
    .init({
      resources,
      lng: initialLng,
      fallbackLng: 'pl',
      defaultNS: 'common',
      interpolation: {
        escapeValue: false,
      },
      react: {
        useSuspense: false,
      },
    });

  return i18n;
}

export function I18nProvider({ children }: { children: ReactNode }) {
  // Initialize with a default instance immediately to avoid warnings
  const [i18nInstance, setI18nInstance] = useState<I18nInstance>(() => 
    createI18nInstance()
  );

  useEffect(() => {
    // Get the language from localStorage or default to 'pl'
    const savedLanguage = typeof window !== 'undefined' 
      ? localStorage.getItem('language') || 'pl'
      : 'pl';

    // Only create a new instance if the language is different
    if (savedLanguage !== i18nInstance.language) {
      const newI18n = createI18nInstance(savedLanguage);
      
      // Save language changes to localStorage
      newI18n.on('languageChanged', (lng) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('language', lng);
        }
      });
      
      setI18nInstance(newI18n);
    } else {
      // Set up language change handler for the existing instance
      i18nInstance.on('languageChanged', (lng) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem('language', lng);
        }
      });
    }
  }, []);

  return <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>;
}
