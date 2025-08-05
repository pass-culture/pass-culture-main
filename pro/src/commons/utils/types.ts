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

// Utils that can be used in typeguard tests
export const itShouldReturnFalseIfGivenUndefinedOrNull = (
  functionToBeTested: (arg: unknown) => boolean
) => {
  it('should return false if the element is null or undefined', () => {
    expect(functionToBeTested(undefined)).toBe(false)
    expect(functionToBeTested(null)).toBe(false)
  })
}

export const isNumber = (value: any) => {
  return typeof value === 'number' && isFinite(value)
}
