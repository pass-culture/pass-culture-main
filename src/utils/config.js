import moment from 'moment'
import 'moment/locale/fr'
import 'moment-duration-format'
import 'moment-timezone'

import { version } from '../../package.json'

moment.locale('fr-fr')

export const {
  ALGOLIA_APPLICATION_ID,
  ALGOLIA_SEARCH_API_KEY,
  ALGOLIA_INDEX_NAME,
  ANDROID_APPLICATION_ID,
  CONTENTFUL_ACCESS_TOKEN,
  CONTENTFUL_ENVIRONMENT,
  CONTENTFUL_SPACE_ID,
  ENVIRONMENT_NAME,
  ID_CHECK_URL,
  IS_DEBUG_PAGE_ACTIVE,
  MAILJET_NOT_YET_ELIGIBLE_LIST_ID,
  MAILJET_PRIVATE_API_KEY,
  MAILJET_PUBLIC_API_KEY,
  MAINTENANCE_PAGE_AVAILABLE,
  MATOMO_GEOLOCATION_GOAL_ID,
  NODE_ENV,
  RECAPTCHA_SITE_KEY,
  SENTRY_SERVER_URL,
  TYPEFORM_URL_CULTURAL_PRACTICES_POLL,
  URL_FOR_MAINTENANCE,
} = process.env

export const APP_VERSION = version
export const PROJECT_NAME = 'pass Culture'
export const IS_DEV = NODE_ENV === 'development'
export const IS_PROD = !IS_DEV

// NOTE: valeur également présente en dur dans:
// - ./webapp/README.md
// - ./webapp/public/MentionsLegalesPass.md
export const SUPPORT_EMAIL = 'support@passculture.app'
export const SUPPORT_EMAIL_SUBJECT = encodeURI('Votre question depuis l’application pass Culture')
export const API_URL = process.env.API_URL || 'http://localhost'

let calculatedLocalhost
if (typeof window !== 'undefined') {
  calculatedLocalhost =
    window.location.hostname === 'localhost' ||
    window.location.hostname === '[::1]' ||
    window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/)
}

export const IS_LOCALHOST = Boolean(calculatedLocalhost)

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined') {
  CALC_ROOT_PATH = `${window.location.protocol}//${document.location.host}`
}

export const ROOT_PATH = CALC_ROOT_PATH || 'http://localhost:3000/'
export const ICONS_URL = `${ROOT_PATH}/icons`
export const ANIMATIONS_URL = `${ROOT_PATH}/animations`
