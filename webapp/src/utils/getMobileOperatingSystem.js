export const getOperatingSystemByUA = userAgent => {
  if (/windows phone/i.test(userAgent)) {
    // Windows Phone must come first because its UA also contains "Android"
    return 'windows_phone'
  }
  if (/android/i.test(userAgent)) {
    return 'android'
  }
  if (/iPad|iPhone|iPod/.test(userAgent) && !window.MSStream) {
    // iOS detection from: http://stackoverflow.com/a/9039885/177710
    return 'ios'
  }
  return 'unknown'
}

export const getMobileOperatingSystem = () => {
  const isDefined = typeof window !== 'undefined' && typeof navigator !== 'undefined'
  if (!isDefined) return 'unknown'
  const userAgent = navigator.userAgent || navigator.vendor || window.opera
  return getOperatingSystemByUA(userAgent)
}

export default getMobileOperatingSystem
