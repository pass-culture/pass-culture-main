/* istanbul ignore file */
const NODE_ENV = import.meta.env.NODE_ENV || 'development'

export const IS_DEV = NODE_ENV === 'development'

export const CGU_URL = 'https://pass.culture.fr/cgu-professionnels/'

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== 'undefined') {
  apiUrlBasedOnDomain = window.location.hostname.includes('beta.gouv')
    ? import.meta.env.VITE_API_URL_OLD
    : import.meta.env.VITE_API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || 'http://localhost'

export const ENVIRONMENT_NAME = import.meta.env.VITE_ENVIRONMENT_NAME
export const ENV_WORDING = import.meta.env.VITE_ENV_WORDING
export const SENTRY_SAMPLE_RATE = import.meta.env.VITE_SENTRY_SAMPLE_RATE
export const SENTRY_SERVER_URL = import.meta.env.VITE_SENTRY_SERVER_URL
export const VITE_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4 = import.meta
  .env.VITE_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4
export const RECAPTCHA_SITE_KEY = import.meta.env.VITE_RECAPTCHA_SITE_KEY
export const WEBAPP_URL = import.meta.env.VITE_WEBAPP_URL

export const URL_FOR_MAINTENANCE =
  import.meta.env.VITE_URL_FOR_MAINTENANCE || ''

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined') {
  CALC_ROOT_PATH = window.location.protocol + '//' + document.location.host
}
export const ROOT_PATH =
  import.meta.env.STORYBOOK_ROOT_PATH ||
  CALC_ROOT_PATH ||
  'http://localhost:3001/'

export const LOGS_DATA = import.meta.env.VITE_LOGS_DATA === 'true'
export const {
  VITE_ALGOLIA_APP_ID: ALGOLIA_APP_ID,
  VITE_ALGOLIA_API_KEY: ALGOLIA_API_KEY,
  VITE_ALGOLIA_COLLECTIVE_OFFERS_INDEX: ALGOLIA_COLLECTIVE_OFFERS_INDEX,
  VITE_ASSETS_URL: ASSETS_URL,
} = import.meta.env
