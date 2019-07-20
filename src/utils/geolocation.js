import { MOBILE_OS } from './config'

export const humanizeRelativeDistance = (
  venueLatitude,
  venueLongitude,
  userLatitude = null,
  userLongitude = null
) => {
  if (!userLatitude || !userLongitude) return '-'

  const distanceInMeters = computeDistanceInMeters(
    userLatitude,
    userLongitude,
    venueLatitude,
    venueLongitude
  )

  return humanizeDistance(distanceInMeters)
}

export function navigationLink(lat, long) {
  // see https://stackoverflow.com/questions/9688607/how-to-open-a-mobile-devices-map-app-when-a-user-clicks-on-a-link
  if (MOBILE_OS === 'ios') {
    return `maps://maps.google.com/maps?daddr=${lat},${long}`
  }

  if (MOBILE_OS === 'android') {
    return `http://maps.google.com/maps?daddr=${lat},${long}`
  }

  return `https://www.openstreetmap.org/#map=18/${lat}/${long}`
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
