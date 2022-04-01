const NODE_ENV = process.env.NODE_ENV || 'development'
// NOTE -> le script PC remplace
// la valeur de `LAST_DEPLOYED_COMMIT`
// par le numéro de commit qui a été deployé
export const LAST_DEPLOYED_COMMIT = '##LAST_DEPLOYED_COMMIT##'

export const IS_DEV = NODE_ENV === 'development'
export const IS_TEST = NODE_ENV === 'test'

export const CGU_URL = 'https://pass.culture.fr/cgu-professionnels/'

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== 'undefined') {
  apiUrlBasedOnDomain = window.location.hostname.includes('beta.gouv')
    ? process.env.API_URL_OLD
    : process.env.API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || 'http://localhost'

export const {
  ENVIRONMENT_NAME,
  ENV_WORDING,
  SENTRY_SAMPLE_RATE,
  SENTRY_SERVER_URL,
  URL_FOR_MAINTENANCE,
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL,
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL,
  DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL,
  ASSETS_URL,
  RECAPTCHA_SITE_KEY,
  WEBAPP_URL,
} = process.env

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined') {
  CALC_ROOT_PATH = window.location.protocol + '//' + document.location.host
}

export const ROOT_PATH = CALC_ROOT_PATH || 'http://localhost:3001/'
