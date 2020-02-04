import getMobileOperatingSystem from '../utils/getMobileOperatingSystem'

export const getHumanizeRelativeDistance = (
  venueLatitude = null,
  venueLongitude = null,
  userLatitude = null,
  userLongitude = null
) => {
  if (!userLatitude || !userLongitude || !venueLatitude || !venueLongitude) return '-'

  const distanceInMeters = computeDistanceInMeters(
    venueLatitude,
    venueLongitude,
    userLatitude,
    userLongitude
  )

  return humanizeDistance(distanceInMeters)
}

export function navigationLink(venueLatitude, venueLongitude, userGeolocation = {}) {
  const mobileOs = getMobileOperatingSystem()

  if (mobileOs === 'ios') {
    return `maps://maps.google.com/maps?daddr=${venueLatitude},${venueLongitude}`
  }

  if (mobileOs === 'android') {
    return `http://maps.google.com/maps?daddr=${venueLatitude},${venueLongitude}`
  }

  if (userGeolocation.latitude !== null && userGeolocation.longitude !== null) {
    return `https://www.openstreetmap.org/directions?route=${userGeolocation.latitude},${userGeolocation.longitude};${venueLatitude},${venueLongitude}`
  } else {
    return `https://www.openstreetmap.org/directions?route=;${venueLatitude},${venueLongitude}`
  }
}

export const computeDistanceInMeters = (latitudeA, longitudeA, latitudeB, longitudeB) => {
  const earthRadiusKm = 6378.137
  const newLatitude = (latitudeB * Math.PI) / 180 - (latitudeA * Math.PI) / 180
  const newLongitude = (longitudeB * Math.PI) / 180 - (longitudeA * Math.PI) / 180
  const a =
    Math.sin(newLatitude / 2) * Math.sin(newLatitude / 2) +
    Math.cos((latitudeA * Math.PI) / 180) *
      Math.cos((latitudeB * Math.PI) / 180) *
      Math.sin(newLongitude / 2) *
      Math.sin(newLongitude / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return earthRadiusKm * c * 1000
}

export const humanizeDistance = distance => {
  if (distance < 30) {
    return `${Math.round(distance)} m`
  }

  if (distance < 100) {
    return `${Math.round(distance / 5) * 5} m`
  }

  if (distance < 1000) {
    return `${Math.round(distance / 10) * 10} m`
  }

  if (distance < 5000) {
    return `${Math.round(distance / 100) / 10} km`
  }

  return `${Math.round(distance / 1000)} km`
}

export const computeToAroundLatLng = geolocation => {
  const { latitude, longitude } = geolocation

  let aroundLatLng = ''
  if (latitude && longitude) {
    aroundLatLng = `${latitude}, ${longitude}`
  }
  return aroundLatLng
}
