import moment from 'moment'
import 'moment/locale/fr'
import 'moment-duration-format'
import 'moment-timezone'

import { version } from '../../package.json'

moment.locale('fr-fr')

export const {
  ENVIRONMENT_NAME,
  MAINTENANCE_PAGE_AVAILABLE,
  NODE_ENV,
  SENTRY_SERVER_URL_FOR_WEBAPP,
  TYPEFORM_URL_CULTURAL_PRACTICES_POLL,
  URL_FOR_MAINTENANCE,
  WEBAPP_ALGOLIA_APPLICATION_ID,
  WEBAPP_ALGOLIA_SEARCH_API_KEY,
  WEBAPP_ALGOLIA_INDEX_NAME
} = process.env
export const APP_VERSION = version
export const PROJECT_NAME = 'pass Culture'
export const IS_DEV = NODE_ENV === 'development'
export const IS_PROD = !IS_DEV
export const WEBAPP_CONTACT_EXTERNAL_PAGE =
  'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'

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
