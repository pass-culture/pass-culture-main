const latLonPattern = /^((-?|\+?)?\d+(\.\d+)?),\s*((-?|\+?)?\d+(\.\d+)?)$/
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
