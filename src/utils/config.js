import moment from 'moment'
import 'moment/locale/fr'
import 'moment-timezone'

moment.locale('fr-fr')

const NODE_ENV = process.env.NODE_ENV || 'development'
const ENV_NAME = process.env.ENVIRONMENT_NAME
// NOTE -> le script PC remplace
// la valeur de `LAST_DEPLOYED_COMMIT`
// par le numéro de commit qui a été deployé
export const LAST_DEPLOYED_COMMIT = '##LAST_DEPLOYED_COMMIT##'

export const IS_DEBUG = true

export const IS_DEV = NODE_ENV === 'development'
export const IS_PROD = !IS_DEV
export const STYLEGUIDE_ACTIVE = ENV_NAME !== 'production' && ENV_NAME !== 'staging'

export const DELETE = '_delete_'

export const HELP_PAGE_URL = 'https://aide.passculture.app/fr/category/acteurs-culturels-1t20dhs/'
export const CGU_URL = 'https://docs.passculture.app/textes-normatifs'

export const API_URL = process.env.API_URL || 'http://localhost'
export const {
  ENVIRONMENT_NAME,
  SENTRY_SERVER_URL,
  URL_FOR_MAINTENANCE,
  MAINTENANCE_PAGE_AVAILABLE,
  DEMARCHES_SIMPLIFIEES_OFFERER_RIB_UPLOAD_PROCEDURE_URL,
  DEMARCHES_SIMPLIFIEES_VENUE_RIB_UPLOAD_PROCEDURE_URL,
} = process.env

function getMobileOperatingSystem() {
  if (typeof window !== 'undefined' && typeof navigator !== 'undefined') {
    let userAgent = navigator.userAgent || navigator.vendor || window.opera

    // Windows Phone must come first because its UA also contains "Android"
    if (/windows phone/i.test(userAgent)) {
      return 'windows_phone'
    }

    if (/android/i.test(userAgent)) {
      return 'android'
    }

    // iOS detection from: http://stackoverflow.com/a/9039885/177710
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
      return 'ios'
    }
    return 'unknown'
  }
}

export const MOBILE_OS = getMobileOperatingSystem()

let calculatedLocalhost
if (typeof window !== 'undefined') {
  calculatedLocalhost =
    window.location.hostname === 'localhost' ||
    // [::1] is the IPv6 localhost address.
    window.location.hostname === '[::1]' ||
    // 127.0.0.1/8 is considered localhost for IPv4.
    window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/)
}

export const IS_LOCALHOST = Boolean(calculatedLocalhost)

let CALC_ROOT_PATH = ''
if (typeof window !== 'undefined' && window.cordova) {
  document.body.className += ' cordova'
  if (MOBILE_OS === 'android') {
    CALC_ROOT_PATH = 'file:///android_asset/www'
    document.body.className += ' cordova-android'
    //document.body.className += ' android-with-statusbar'
  } else if (MOBILE_OS === 'ios') {
    //TODO
    document.body.className += ' cordova-ios'
    // CALC_ROOT_PATH = window.location.href.split('/').slice(0, 10).join('/')
    CALC_ROOT_PATH = window.location.href.match(/file:\/\/(.*)\/www/)[0]
  }
  window.addEventListener('keyboardWillShow', function() {
    console.log('Keyboard show')
    document.body.className += ' softkeyboard'
  })
  window.addEventListener('keyboardWillHide', function() {
    console.log('Keyboard Hide')
    document.body.className = document.body.className
      .split(' ')
      .filter(c => c !== 'softkeyboard')
      .join(' ')
  })
} else {
  if (typeof window !== 'undefined') {
    document.body.className += ' web'
    CALC_ROOT_PATH = window.location.protocol + '//' + document.location.host
  }
}

export const ROOT_PATH = CALC_ROOT_PATH || 'http://localhost:3001/'

export const DEFAULT_TO = '/accueil'
