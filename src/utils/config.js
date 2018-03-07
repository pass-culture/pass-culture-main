const { NODE_ENV } = process.env

export const IS_DEV = NODE_ENV === 'development'

export const NEW = '_new_'

export const API_URL = IS_DEV ? 'http://localhost'
                              : 'https://pc-api.btmx.fr'

export const BROWSER_URL = IS_DEV ? 'http://localhost:3000'
                                  : 'https://pc.btmx.fr'

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

