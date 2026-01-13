import type { AnyObject } from './types'

/**
 * Returns the keys of the given object as an array of its key types.
 *
 * This is a typed version of Object.keys
 *
 * @param obj - The object whose keys should be retrieved.
 * @returns An array of the object's keys, typed as (keyof O)[]
 */
export function objectKeys<O extends AnyObject>(
  obj: O
  // biome-ignore lint/suspicious/noExplicitAny: Trick to forces TypeScript to distribute generic type in union (instead of intersection)
): (O extends any ? keyof O : never)[] {
  // biome-ignore lint/suspicious/noExplicitAny: see above
  return Object.keys(obj) as any
}

/**
 * Returns a typed array of the object's own enumerable string-keyed property [key, value] pairs.
 *
 * This is a typed version of Object.entries
 *
 * @param obj - The object whose entries are to be returned.
 * @returns A typed array of [key, value] pairs from the object.
 */
export function objectEntries<O extends AnyObject>(
  obj: O
): [keyof O, O[keyof O]][] {
  return Object.entries(obj) as [keyof O, O[keyof O]][]
}

/**
 * Transforms a list of typed key-value pairs into an object of type O.
 *
 * This is a typed version of Object.fromEntries
 *
 * @param entries - A typed array of [key, value] pairs to convert into an object.
 * @returns An object of type O composed from the given entries.
 */
export function objectFromEntries<O extends AnyObject>(
  entries: [keyof O, O[keyof O]][]
): O {
  return Object.fromEntries(entries) as O
}
