/* istanbul ignore file */
export const IS_DEV = process.env.MODE === 'development'

export const CGU_URL = 'https://pass.culture.fr/cgu-professionnels/'

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== 'undefined') {
  apiUrlBasedOnDomain = window.location.hostname.includes('beta.gouv')
    ? process.env.VITE_API_URL_OLD
    : process.env.VITE_API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || 'http://localhost'

export const ENVIRONMENT_NAME = process.env.MODE
export const ENV_WORDING = process.env.VITE_ENV_WORDING
export const SENTRY_SAMPLE_RATE = process.env.VITE_SENTRY_SAMPLE_RATE
export const SENTRY_SERVER_URL = process.env.VITE_SENTRY_SERVER_URL
export const DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4 =
  process.env.VITE_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4
export const RECAPTCHA_SITE_KEY = process.env.VITE_RECAPTCHA_SITE_KEY
export const WEBAPP_URL = process.env.VITE_WEBAPP_URL
export const URL_FOR_MAINTENANCE = process.env.VITE_URL_FOR_MAINTENANCE || ''

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined') {
  CALC_ROOT_PATH = window.location.protocol + '//' + document.location.host
}
export const ROOT_PATH =
  process.env.STORYBOOK_ROOT_PATH || CALC_ROOT_PATH || 'http://localhost:3001/'

export const LOGS_DATA = process.env.VITE_LOGS_DATA === 'true'
export const ALGOLIA_APP_ID = process.env.VITE_ALGOLIA_APP_ID
export const ALGOLIA_API_KEY = process.env.VITE_ALGOLIA_API_KEY
export const ALGOLIA_COLLECTIVE_OFFERS_INDEX =
  process.env.VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX

export const FIREBASE_API_KEY =
  process.env.VITE_FIREBASE_PUBLIC_API_KEY ||
  'AIzaSyAhXSv-Wk5I3hHAga5KhCe_SUhdmY-2eyQ'
export const FIREBASE_AUTH_DOMAIN =
  process.env.VITE_FIREBASE_AUTH_DOMAIN || 'passculture-pro.firebaseapp.com'
export const FIREBASE_PROJECT_ID =
  process.env.VITE_FIREBASE_PROJECT_ID || 'passculture-pro'
export const FIREBASE_STORAGE_BUCKET =
  process.env.VITE_FIREBASE_STORAGE_BUCKET || 'passculture-pro.appspot.com'
export const FIREBASE_MESSAGING_SENDER_ID =
  process.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '412444774135'
export const FIREBASE_APP_ID =
  process.env.VITE_FIREBASE_APP_ID ||
  '1:412444774135:web:0cd1b28CCCC6f9d6c54df2'
export const FIREBASE_MEASUREMENT_ID =
  process.env.VITE_FIREBASE_MEASUREMENT_ID || 'G-FBPYNQPRF6'
