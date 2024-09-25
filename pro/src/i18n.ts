import { use } from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'

import { localStorageAvailable } from 'utils/localStorageAvailable'

import common_en from './locales/en/common.json'
import common_fr from './locales/fr/common.json'
import common_pt from './locales/pt/common.json'

const localStorageLanguage = localStorageAvailable()
  ? localStorage.getItem('i18nextLng')
  : null

// eslint-disable-next-line @typescript-eslint/no-floating-promises
use(initReactI18next)
  .use(LanguageDetector)
  .init({
    ...(localStorageLanguage && { lng: localStorageLanguage }),
    interpolation: { escapeValue: false },
    supportedLngs: ['en', 'fr', 'pt'],
    // supportedLngs: appConfig.languages.supportedLngs,
    // fallbackLng: appConfig.languages.fallbackLng,
    resources: {
      en: {
        common: common_en,
      },
      fr: {
        common: common_fr,
      },
      pt: {
        common: common_pt,
      },
    },
  })
