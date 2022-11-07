export const hasProperty = <T extends string>(
  element: unknown,
  property: T
): element is Record<T, unknown> => {
  if (element === undefined || element === null) {
    return false
  }

  return Boolean(Object.prototype.hasOwnProperty.call(element, property))
}

// Utils that can be used in typeguard tests
export const itShouldReturnFalseIfGivenUndefinedOrNull = (
  functionToBeTested: (arg: unknown) => boolean
) => {
  it('should return false if the element is null or undefined', () => {
    expect(functionToBeTested(undefined)).toBe(false)
    expect(functionToBeTested(null)).toBe(false)
  })
}
