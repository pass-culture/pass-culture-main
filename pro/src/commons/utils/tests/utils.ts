// Utils that can be used in typeguard tests
export const itShouldReturnFalseIfGivenUndefinedOrNull = (
  functionToBeTested: (arg: unknown) => boolean
) => {
  it('should return false if the element is null or undefined', () => {
    expect(functionToBeTested(undefined)).toBe(false)
    expect(functionToBeTested(null)).toBe(false)
  })
}
