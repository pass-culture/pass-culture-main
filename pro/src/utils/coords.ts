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
// http://regexpal.com/?flags=gim&regex=^%28-%3F\d%2B%28%3F%3A\.\d%2B%29%3F%29[%C2%B0%3Ad]%3F\s%3F%28%3F%3A%28\d%2B%28%3F%3A\.\d%2B%29%3F%29[%27%E2%80%B2%3A]%3F\s%3F%28%3F%3A%28\d%2B%28%3F%3A\.\d%2B%29%3F%29[%22%E2%80%B3]%3F%29%3F%29%3F\s%3F%28[NSEW]%29%3F&input=40%3A26%3A46N%2C79%3A56%3A55W%0A40%3A26%3A46.302N%2079%3A56%3A55.903W%0A40%C2%B026%E2%80%B247%E2%80%B3N%2079%C2%B058%E2%80%B236%E2%80%B3W%0A40d%2026%E2%80%B2%2047%E2%80%B3%20N%2079d%2058%E2%80%B2%2036%E2%80%B3%20W%0A40.446195N%2079.948862W%0A40.446195%2C%20-79.948862%0A40%C2%B0%2026.7717%2C%20-79%C2%B0%2056.93172%0A
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
