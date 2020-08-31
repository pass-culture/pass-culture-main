import { formatPublicName } from '../formatPublicName'

describe('src | components | formatPublicName', () => {
  it('should return public name when less than 15 characters and no space is included', () => {
    // given
    const publicName = "Jeanjean"

    // when
    const result = formatPublicName(publicName)

    // then
    expect(result).toBe('Jeanjean')
  })

  it('should return public name when less than 15 characters and including a space', () => {
    // given
    const publicName = "Jeanne Valjeann"

    // when
    const result = formatPublicName(publicName)

    // then
    expect(result).toBe('Jeanne Valjeann')
  })

  it('should return first part of public name when it includes a space and is more than 15 characters', () => {
    // given
    const publicName = "Jean Valjean de la comté lointaine"

    // when
    const result = formatPublicName(publicName)

    // then
    expect(result).toBe('Jean')
  })

  it('should return public name when it includes no space and is more than 15 characters', () => {
    // given
    const publicName = "IronManLeMeilleurDesHeros"

    // when
    const result = formatPublicName(publicName)

    // then
    expect(result).toBe('IronManLeMeilleurDesHeros')
  })
})
