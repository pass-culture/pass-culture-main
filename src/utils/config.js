const { NODE_ENV } = process.env

export const IS_DEBUG = true

export const IS_DEV = NODE_ENV === 'development'
export const IS_PROD = !IS_DEV

export const NEW = '_new_'

export const API_URL = IS_DEV ? 'http://localhost'
                              : 'https://api.passculture.beta.gouv.fr'

export const BROWSER_URL = IS_DEV ? 'http://localhost:3000'
                                  : 'https://app.passculture.beta.gouv.fr'

export const THUMBS_URL = IS_DEV
  ? `${API_URL}/static/object_store_data/thumbs`
  : `${API_URL}/static/object_store_data/thumbs`

function getMobileOperatingSystem() {
  var userAgent = navigator.userAgent || navigator.vendor || window.opera;

      // Windows Phone must come first because its UA also contains "Android"
    if (/windows phone/i.test(userAgent)) {
        return "windows_phone";
    }

    if (/android/i.test(userAgent)) {
        return "android";
    }

    // iOS detection from: http://stackoverflow.com/a/9039885/177710
    if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
        return "ios";
    }

    return "unknown";
}

export const MOBILE_OS = getMobileOperatingSystem()

export const IS_LOCALHOST = Boolean(
  window.location.hostname === 'localhost' ||
    // [::1] is the IPv6 localhost address.
    window.location.hostname === '[::1]' ||
    // 127.0.0.1/8 is considered localhost for IPv4.
    window.location.hostname.match(
      /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
    )
);

export const ROOT_PATH = Boolean(window.cordova) ? window.cordova.file.applicationDirectory : '';
