const latLonPattern = /^(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)$/

const dmsLatPattern = /^(\d+)[°\s]\s*(\d+)['\s]\s*([\d.,]+)["\s]?\s*([NS])\s+/i
const dmsLonPattern = /^(\d+)[°\s]\s*(\d+)['\s]\s*([\d.,]+)["\s]?\s*([EW])$/i

function isValidLatLon(coords: string): boolean {
  const match = new RegExp(latLonPattern).exec(coords.trim())
  if (!match) return false

  const lat = Number.parseFloat(match[1])
  const lon = Number.parseFloat(match[2])

  return Math.abs(lat) <= 90 && Math.abs(lon) <= 180
}

function isValidDMS(coords: string): boolean {
  const trimmed = coords.trim()

  const latMatch = new RegExp(dmsLatPattern).exec(trimmed)
  if (!latMatch) return false

  const remaining = trimmed.slice(latMatch[0].length)
  const lonMatch = new RegExp(dmsLonPattern).exec(remaining)
  if (!lonMatch) return false

  const [_, latD, latM, latS] = latMatch
  const [__, lonD, lonM, lonS] = lonMatch

  const latDeg = Number.parseInt(latD, 10)
  const latMin = Number.parseInt(latM, 10)
  const latSec = Number.parseFloat(latS.replace(',', '.'))

  const lonDeg = Number.parseInt(lonD, 10)
  const lonMin = Number.parseInt(lonM, 10)
  const lonSec = Number.parseFloat(lonS.replace(',', '.'))

  if (latMin >= 60 || latSec >= 60 || lonMin >= 60 || lonSec >= 60) return false
  if (latDeg > 90 || (latDeg === 90 && (latMin > 0 || latSec > 0))) return false
  if (lonDeg > 180 || (lonDeg === 180 && (lonMin > 0 || lonSec > 0)))
    return false

  return true
}

/**
 * Check if a string is a valid coordinate
 * @param coords Coordinate string
 * @returns boolean if valid coordinate
 * @example
 * checkCoords('48.853320, 2.348979')
 * // => true
 * checkCoords(`48°51'12.0"N 2°20'56.3"E`)
 * // => true
 * checkCoords('foobar')
 * // => false
 */
export const checkCoords = (coords: string): boolean => {
  return isValidLatLon(coords) || isValidDMS(coords)
}

/**
 * Get the type of coordinates
 * @param coords Coordinate string
 * @returns 'DMS' | 'DD' | 'unknown'
 * @example
 * getCoordsType('48.853320, 2.348979')
 * // => 'DD'
 * getCoordsType(`48°51'12.0"N 2°20'56.3"E`)
 * // => 'DMS'
 * getCoordsType('foobar')
 * // => 'unknown'
 */
export const getCoordsType = (coords: string): 'DMS' | 'DD' | 'unknown' => {
  if (!coords) {
    return 'unknown'
  }

  if (isValidLatLon(coords)) {
    return 'DD'
  }

  if (isValidDMS(coords)) {
    return 'DMS'
  }

  return 'unknown'
}

const numberPattern = /-?[\d.]+/g
const hemispherePattern = /[NSEW]/i

/**
 * Parses a Degrees Minutes Seconds string into a Decimal Degrees number.
 * @param {string} dmsStr A string containing a coordinate in either DMS or DD format.
 * @return {Number} If dmsStr is a valid coordinate string, the value in decimal degrees will be returned. Otherwise NaN will be returned.
 */
export function parseDms(dmsStr: string): number {
  if (!dmsStr) return Number.NaN

  const hemiMatch = new RegExp(hemispherePattern).exec(dmsStr)
  const hemisphere = hemiMatch ? hemiMatch[0] : null

  const matches = dmsStr.match(numberPattern)
  if (!matches || matches.length === 0) return Number.NaN

  const degrees = Number(matches[0])
  const minutes = matches[1] ? Number(matches[1]) / 60 : 0
  const seconds = matches[2] ? Number(matches[2]) / 3600 : 0

  if (Number.isNaN(degrees)) return Number.NaN

  if (hemisphere !== null && /[SW]/i.test(hemisphere)) {
    return -Math.abs(degrees) - minutes - seconds
  }

  return degrees + minutes + seconds
}
