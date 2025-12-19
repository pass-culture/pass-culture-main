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

export type PartialBy<T extends AnyObject, K extends keyof T> = Partial<
  Pick<T, K>
> &
  Omit<T, K>

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
