export type AnyObject = {
  // biome-ignore lint/suspicious/noExplicitAny: This is a placeholder for cases that can't be typed more specifically.
  [key: string]: any
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

export const hasProperties = <T extends string>(
  element: unknown,
  properties: T[]
): element is Record<T, unknown> =>
  properties.every((property) => hasProperty(element, property))

export const isNumber = (value: any) => {
  return typeof value === 'number' && isFinite(value)
}
