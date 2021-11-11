import { addModifierString } from '../addModifierString'

describe('addModifierString', () => {
  it('does not add property named __modifiers__ to empty array of objects', () => {
    // Given
    const value = []
    const expected = []

    // When
    const result = addModifierString()(value)

    // Then
    expect(result).toStrictEqual(expected)
  })

  it('add property named __modifiers__ to array of objects', () => {
    // Given
    const value = [{ prop: 'prop' }]
    const expected = [{ __modifiers__: ['selectBookables'], prop: 'prop' }]

    // When
    const result = addModifierString()(value)

    // Then
    expect(result).toStrictEqual(expected)
  })
})
