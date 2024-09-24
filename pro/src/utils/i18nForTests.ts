import { use } from 'i18next'
import { initReactI18next } from 'react-i18next'

import common_fr from '../locales/fr/common.json'

// eslint-disable-next-line @typescript-eslint/no-floating-promises
use(initReactI18next).init({
  interpolation: { escapeValue: false },
  lng: 'fr',
  // supportedLngs: appConfig.languages.supportedLngs,
  // fallbackLng: appConfig.languages.fallbackLng,
  resources: {
    fr: {
      common: common_fr,
    },
  },
})
