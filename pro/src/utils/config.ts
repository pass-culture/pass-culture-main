/* istanbul ignore file */
export const IS_DEV = import.meta.env.MODE === 'development'

export const CGU_URL = 'https://pass.culture.fr/cgu-professionnels/'

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== 'undefined') {
  apiUrlBasedOnDomain = window.location.hostname.includes('beta.gouv')
    ? import.meta.env.VITE_API_URL_OLD
    : import.meta.env.VITE_API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || 'http://localhost'

export const ENVIRONMENT_NAME = import.meta.env.MODE
export const SENTRY_SAMPLE_RATE = import.meta.env.VITE_SENTRY_SAMPLE_RATE ?? '0'
export const SENTRY_SERVER_URL = import.meta.env.VITE_SENTRY_SERVER_URL
export const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY ?? ''
export const WEBAPP_URL = import.meta.env.VITE_WEBAPP_URL
export const URL_FOR_MAINTENANCE =
  import.meta.env.VITE_URL_FOR_MAINTENANCE || ''
export const LOGS_DATA = import.meta.env.VITE_LOGS_DATA === 'true'

export const ALGOLIA_APP_ID = import.meta.env.VITE_ALGOLIA_APP_ID ?? ''
export const ALGOLIA_API_KEY = import.meta.env.VITE_ALGOLIA_API_KEY ?? ''
export const ALGOLIA_COLLECTIVE_OFFERS_INDEX =
  import.meta.env.VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX ?? ''
export const ALGOLIA_COLLECTIVE_OFFERS_SUGGESTIONS_INDEX =
  import.meta.env.VITE_ALGOLIA_COLLECTIVE_OFFERS_SUGGESTIONS_INDEX ?? ''

export const FIREBASE_API_KEY =
  import.meta.env.VITE_FIREBASE_PUBLIC_API_KEY ||
  'AIzaSyAhXSv-Wk5I3hHAga5KhCe_SUhdmY-2eyQ'
export const FIREBASE_AUTH_DOMAIN =
  import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'passculture-pro.firebaseapp.com'
export const FIREBASE_PROJECT_ID =
  import.meta.env.VITE_FIREBASE_PROJECT_ID || 'passculture-pro'
export const FIREBASE_STORAGE_BUCKET =
  import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'passculture-pro.appspot.com'
export const FIREBASE_MESSAGING_SENDER_ID =
  import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '412444774135'
export const FIREBASE_APP_ID =
  import.meta.env.VITE_FIREBASE_APP_ID ||
  '1:412444774135:web:0cd1b28CCCC6f9d6c54df2'
export const FIREBASE_MEASUREMENT_ID =
  import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || 'G-FBPYNQPRF6'
export const DS_BANK_ACCOUNT_PROCEDURE_ID = import.meta.env
  .VITE_DEMARCHES_SIMPLIFIEES_BANK_ACCOUNT_PROCEDURE_ID
