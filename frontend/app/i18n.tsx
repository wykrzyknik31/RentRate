'use client';

import { createInstance } from 'i18next';
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

export function I18nProvider({ children }: { children: ReactNode }) {
  const [i18nInstance, setI18nInstance] = useState<any>(null);

  useEffect(() => {
    const i18n = createInstance();
    
    // Get the language from localStorage or default to 'pl'
    const savedLanguage = typeof window !== 'undefined' 
      ? localStorage.getItem('language') || 'pl'
      : 'pl';

    i18n
      .use(initReactI18next)
      .init({
        resources,
        lng: savedLanguage,
        fallbackLng: 'pl',
        defaultNS: 'common',
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

    setI18nInstance(i18n);
  }, []);

  if (!i18nInstance) {
    return <>{children}</>;
  }

  return <I18nextProvider i18n={i18nInstance}>{children}</I18nextProvider>;
}
