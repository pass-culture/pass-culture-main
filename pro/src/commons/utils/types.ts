export type AnyObject = {
  // biome-ignore lint/suspicious/noExplicitAny: This is a placeholder for cases that can't be typed more specifically.
  [key: string]: any
}

/**
 * Makes all properties of an object both defined and non-omittable.
 *
 * @example
 * ```ts
 * type Foo = {
 *   a?: number
 *   b: string | undefined
 *   c?: string | undefined
 * }
 *
 * type Bar = Defined<Foo>
 * // Result:
 * // {
 * //   a: number
 * //   b: string
 * //   c: string
 * // }
 * ```
 */
export type Defined<T extends AnyObject> = {
  [K in keyof T]-?: T[K] extends undefined ? never : T[K]
}

/**
 * Makes all properties of an object omittable, except for those in `K`.
 *
 * @example
 * ```ts
 * interface Foo {
 *   id: number
 *   name: string
 * }
 *
 * type Bar = PartialExcept<Foo, 'id'>
 * // Result:
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
 * Makes all properties of an object nullable.
 *
 * @example
 * ```ts
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
 * ```
 */
export type Nullable<T extends AnyObject> = {
  [P in keyof T]: T[P] | null
}

/**
 * Picks the properties of an object, and makes them both defined and non-omittable.
 *
 * @description
 * This is useful for real PATCHes where a form only covers a subset of a Backend route's request body.
 *
 * @example
 * ```ts
 * type FooRequestBody = {
 *   a?: boolean
 *   b?: number
 *   c?: string
 * }
 *
 * type FooRequestBodyBarPatch = PickDefined<FooRequestBody, 'a' | 'b'>
 * // Result:
 * // {
 * //   a: boolean
 * //   b: number
 * // }
 * ```
 */
export type PickDefined<T extends AnyObject, K extends keyof T> = Pick<
  Defined<T>,
  K
>

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
