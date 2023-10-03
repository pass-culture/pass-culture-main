interface Coordinates {
  latitude: number
  longitude: number
}

const EARTH_RADIUS_KM = 6378.137

export const getHumanizeRelativeDistance = (
  from: Coordinates,
  to: Coordinates
): string => {
  const distanceInMeters = computeDistanceInMeters(from, to)
  return humanizeDistance(distanceInMeters).replace('.', ',')
}

const computeDistanceInMeters = (from: Coordinates, to: Coordinates) => {
  const newLat = (to.latitude * Math.PI) / 180 - (from.latitude * Math.PI) / 180
  const newLng =
    (to.longitude * Math.PI) / 180 - (from.longitude * Math.PI) / 180
  const a =
    Math.sin(newLat / 2) * Math.sin(newLat / 2) +
    Math.cos((from.latitude * Math.PI) / 180) *
      Math.cos((to.latitude * Math.PI) / 180) *
      Math.sin(newLng / 2) *
      Math.sin(newLng / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return EARTH_RADIUS_KM * c * 1000
}

const humanizeDistance = (distance: number) => {
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

  const distanceKm = Math.round(distance / 1000)
  return `${distanceKm > 900 ? '900+' : distanceKm} km`
}
