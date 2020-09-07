import { formatToReadableString } from './formatToReadableString'

describe('src | utils | strings | formatToReadableString', () => {
  it('should return a string with a first capitalized letter only when no capitalized letter', () => {
    // given
    const input = "avengers"

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toStrictEqual("Avengers")
  })

  it('should return a string with lowercased letters except the first letter', () => {
    // given
    const input = "AVENGERS"

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toStrictEqual("Avengers")
  })

  it('should return a string with lowercased letters and two words with capitalized letters', () => {
    // given
    const input = "AVENGERS L'âge d'ultron"

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toStrictEqual("Avengers l'âge d'ultron")
  })

  it('should not capitalize coordination words', () => {
    // given
    const input = "AVENGERS les supers héros"

    // when
    const result = formatToReadableString(input)

    // then
    expect(result).toStrictEqual("Avengers les supers héros")
  })
})
