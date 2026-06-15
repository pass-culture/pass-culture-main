import type { Entries } from './'

/**
 * Returns a typed array of the keys of a ReadonlyMap.
 * @param map - The map to get the keys from.
 * @returns An array of the keys of the map.
 */
export function getMapKeys<K, V>(map: ReadonlyMap<K, V>): K[] {
  return [...map.keys()]
}

/**
 * Transforms a ReadonlyMap into an array of select option objects with label and value.
 * @param map - The map to transform.
 * @returns An array of objects with { label, value } for use as select options.
 */
export function toSelectOptions<K, V>(
  map: ReadonlyMap<K, V>
): { label: V; value: K }[] {
  return [...map.entries()].map(([k, v]) => ({ label: v, value: k }))
}

/**
 * Returns a function that sorts an array of [key, value] entries by their value, using locale-aware string comparison.
 *
 * @param locale - The BCP 47 language tag (e.g., 'fr-FR') used for locale-aware comparison.
 * @returns A function that takes an array of [string, string] entries and returns the array sorted by value.
 */
export function sortEntriesByValue(locale: string) {
  const compareFn = new Intl.Collator(locale).compare
  return <E extends Entries<string, string>>(val: E): E => {
    return val.sort((a, b) => compareFn(a[1], b[1]))
  }
}

/**
 * Returns a function that moves the specified key to the end of an array of [key, value] entries.
 *
 * Useful for option lists where a specific entry (eg: "OTHER") should always display last.
 *
 * @param key - The key to move to the end of the array.
 * @returns A function that takes an array of [string, string] entries and returns a new array,
 *          with the specified key/value entry at the end if it exists.
 */
export function putKeyAtTheEnd(key: string) {
  return <E extends Entries<string, string>>(val: E): E => {
    const keyIndex = val.findIndex(([k]) => k === key)
    const keyValue = val[keyIndex]
    if (keyIndex > -1) {
      val.splice(keyIndex, 1)
      return val.concat([keyValue]) as E
    }
    return val
  }
}
