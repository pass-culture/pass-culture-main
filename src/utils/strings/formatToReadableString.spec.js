import { formatToReadableString } from './formatToReadableString'

describe('src | utils | strings | formatToReadableString', () => {
  it('should return a string with a first capitalized letter when no capitalized letter', () => {
    // given
    const input = "avengers"

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toStrictEqual("Avengers")
  })

  it('should return given input when null', () => {
    // given
    const input = null

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toBeNull()
  })
})
