interface Coordinates {
  latitude: number
  longitude: number
}

enum DistanceUnitCoef {
  Meters = 1,
  Kilometers = 1000,
}

const EARTH_RADIUS = 6378137 // meters

const toRad = (value: number) => (value * Math.PI) / 180

export const getDistance = (
  from: Coordinates,
  to: Coordinates,
  unitCoef: DistanceUnitCoef = DistanceUnitCoef.Kilometers
) => {
  const distanceInMeters =
    Math.acos(
      Math.sin(toRad(to.latitude)) * Math.sin(toRad(from.latitude)) +
        Math.cos(toRad(to.latitude)) *
          Math.cos(toRad(from.latitude)) *
          Math.cos(toRad(from.longitude) - toRad(to.longitude))
    ) * EARTH_RADIUS

  return Math.round(distanceInMeters / unitCoef)
}
