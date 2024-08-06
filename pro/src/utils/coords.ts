const latLonPattern =
  /^(-?(?:[1-8]?\d(?:\.\d+)?|90(?:\.0+)?|-90(?:\.0+)?))\s*,\s*(-?(?:1[0-7]\d|\d{1,2})(?:\.\d+)?|180(?:\.0+)?|-180(?:\.0+)?)$/

const DMSPattern =
  /^(?:90|(?:[0-8]{0,1}[0-9]))[°\s](?:[0-5]{0,1}[0-9])['\s](?:[0-5]{0,1}[0-9](?:[.,]\d{1,5})?)["\s]{0,1}[NS]\s(?:180|(?:1[0-7]{1}[0-9]{1})|(?:0?[0-9]{1}[0-9]{1})|(?:[0-9]{1}))[°\s](?:[0-5]{0,1}[0-9])['\s](?:[0-5]{0,1}[0-9](?:[.,]\d{1,5})?)["\s]{0,1}[EW]$/

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
  return latLonPattern.test(coords) || DMSPattern.test(coords)
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
  if (latLonPattern.test(coords)) {
    return 'DD'
  }

  if (DMSPattern.test(coords)) {
    return 'DMS'
  }

  return 'unknown'
}

// Matches DMS DmsCoordinates
export const dmsRe =
  /^(-?\d+(?:\.\d+)?)[°:d]?\s?(?:(\d+(?:\.\d+)?)['′ʹ:]?\s?(?:(\d+(?:\.\d+)?)["″ʺ]?)?)?\s?([NSEW])?/i
// Results of match will be [full coords string, Degrees, minutes (if any), seconds (if any), hemisphere (if any)]
// E.g., ["40:26:46.302N", "40", "26", "46.302", "N"]
// E.g., ["40.446195N", "40.446195", undefined, undefined, "N"]

/**
 * Parses a Degrees Minutes Seconds string into a Decimal Degrees number.
 * @param {string} dmsStr A string containing a coordinate in either DMS or DD format.
 * @return {Number} If dmsStr is a valid coordinate string, the value in decimal degrees will be returned. Otherwise NaN will be returned.
 */
export function parseDms(dmsStr: string): number {
  let output = NaN
  const dmsMatch = dmsRe.exec(dmsStr)
  if (dmsMatch) {
    const degrees = Number(dmsMatch[1])

    const minutes =
      typeof dmsMatch[2] !== 'undefined' ? Number(dmsMatch[2]) / 60 : 0
    const seconds =
      typeof dmsMatch[3] !== 'undefined' ? Number(dmsMatch[3]) / 3600 : 0
    const hemisphere = dmsMatch[4] || null
    if (hemisphere !== null && /[SW]/i.test(hemisphere)) {
      output = -Math.abs(degrees) - minutes - seconds
    } else {
      output = degrees + minutes + seconds
    }
  }
  return output
}
