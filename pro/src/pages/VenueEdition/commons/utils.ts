import type { AnyObject } from '@/commons/utils/types'

/**
 * Returns the keys of the given object as an array of its key types.
 *
 * @param obj - The object whose keys should be retrieved.
 * @returns An array of the object's keys, typed as (keyof O)[]
 */
export function objectKeys<O extends AnyObject>(obj: O): (keyof O)[] {
  return Object.keys(obj) as (keyof O)[]
}
