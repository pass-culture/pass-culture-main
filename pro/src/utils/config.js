const NODE_ENV = process.env.NODE_ENV || 'development'
// NOTE -> le script PC remplace
// la valeur de `LAST_DEPLOYED_COMMIT`
// par le numéro de commit qui a été deployé
export const LAST_DEPLOYED_COMMIT = '##LAST_DEPLOYED_COMMIT##'

export const IS_DEV = NODE_ENV === 'development'

export const CGU_URL = 'https://pass.culture.fr/cgu-professionnels/'

// FIXME : Remove when transition to new domain is done
let apiUrlBasedOnDomain
if (typeof window !== 'undefined') {
  apiUrlBasedOnDomain = window.location.hostname.includes('beta.gouv')
    ? process.env.REACT_APP_API_URL_OLD
    : process.env.REACT_APP_API_URL_NEW
}
export const API_URL = apiUrlBasedOnDomain || 'http://localhost'

export const ENVIRONMENT_NAME = process.env.REACT_APP_ENVIRONMENT_NAME
export const ENV_WORDING = process.env.REACT_APP_ENV_WORDING
export const SENTRY_SAMPLE_RATE = process.env.REACT_APP_SENTRY_SAMPLE_RATE
export const SENTRY_SERVER_URL = process.env.REACT_APP_SENTRY_SERVER_URL
export const URL_FOR_MAINTENANCE = process.env.REACT_APP_URL_FOR_MAINTENANCE
export const DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL =
  process.env.REACT_APP_DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL
export const DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL =
  process.env.REACT_APP_DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL
export const DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL =
  process.env
    .REACT_APP_DEMARCHES_SIMPLIFIEES_BUSINESS_UNIT_RIB_UPLOAD_PROCEDURE_URL
export const REACT_APP_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4 =
  process.env.REACT_APP_DEMARCHES_SIMPLIFIEES_RIB_VENUE_PROCEDURE_ID_V4
export const ASSETS_URL = process.env.REACT_APP_ASSETS_URL
export const RECAPTCHA_SITE_KEY = process.env.REACT_APP_RECAPTCHA_SITE_KEY
export const WEBAPP_URL = process.env.REACT_APP_WEBAPP_URL

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined') {
  CALC_ROOT_PATH = window.location.protocol + '//' + document.location.host
}

export const ROOT_PATH =
  process.env.STORYBOOK_ROOT_PATH || CALC_ROOT_PATH || 'http://localhost:3001/'
