export type AnyObject = {
  // biome-ignore lint/suspicious/noExplicitAny: This is a placeholder for cases that can't be typed more specifically.
  [key: string]: any
}

export type Defined<T extends AnyObject> = {
  [K in keyof T]-?: T[K] extends undefined ? never : T[K]
}

/**
 * Makes all properties in `T` optional, except for those in `K` which are required.
 *
 * @example
 * ```ts
 * interface Foo {
 *   id: number
 *   name: string
 * }
 *
 * type Bar = PartialExcept<Foo, 'id'>
 * // Equivalent to:
 * // {
 * //   id: number
 * //   name?: string
 * // }
 * ```
 */
export type PartialExcept<T extends AnyObject, K extends keyof T> = Partial<
  Omit<T, K>
> &
  Pick<T, K>

/**
 * Makes all properties of a given object type nullable.
 *
 * @example
 * interface Foo {
 *   a: number
 *   b: string
 * }
 *
 * type NullableFoo = Nullable<Foo>
 * // Result:
 * // {
 * //   a: number | null;
 * //   b: string | null;
 * // }
 *
 * @template T - The object type whose properties will be made nullable.
 */
export type Nullable<T extends AnyObject> = {
  [P in keyof T]: T[P] | null
}

export const hasProperty = <T extends string>(
  element: unknown,
  property: T
): element is Record<T, unknown> => {
  if (element === undefined || element === null) {
    return false
  }

  // biome-ignore lint/suspicious/noPrototypeBuiltins: We cannot use hasOwn due to lack of support
  return Boolean(element.hasOwnProperty(property))
}

export const isNumber = (value: unknown) => {
  return typeof value === 'number' && Number.isFinite(value)
}
