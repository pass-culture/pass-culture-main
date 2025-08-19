export type AnyObject = {
  // biome-ignore lint/suspicious/noExplicitAny: This is a placeholder for cases that can't be typed more specifically.
  [key: string]: any
}

/**
 * Used to force a type to be defined within `as` declarations.
 *
 * TODO (igabriele, 2025-08-19): We should enable `exactOptionalPropertyTypes` in TSConfig to avoid this kind of hack.
 */
export type Defined<T extends AnyObject> = {
  [K in keyof T]: T[K] extends undefined ? never : T[K]
}

/** Props can be undefined but not omitted contrary to `Partial<T>`. */
export type Undefinedable<T extends AnyObject> = {
  [K in keyof T]: T[K] | undefined
}

export const hasProperty = <T extends string>(
  element: unknown,
  property: T
): element is Record<T, unknown> => {
  if (element === undefined || element === null) {
    return false
  }

  return Boolean(Object.hasOwn(element, property))
}

export const hasProperties = <T extends string>(
  element: unknown,
  properties: T[]
): element is Record<T, unknown> =>
  properties.every((property) => hasProperty(element, property))

export const isNumber = (value: any) => {
  return typeof value === 'number' && isFinite(value)
}
