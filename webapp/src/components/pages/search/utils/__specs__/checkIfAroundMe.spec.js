import { checkIfSearchAround } from '../checkIfSearchAround'

describe('utils | checkIfSearchAround', () => {
  it('should return oui when is search around me', () => {
    const searchAround = {
      everywhere: false,
      place: false,
      user: true,
    }

    // when
    const result = checkIfSearchAround(searchAround)

    // then
    expect(result).toBe('oui')
  })

  it('should return oui when is search around place', () => {
    const searchAround = {
      everywhere: false,
      place: true,
      user: false,
    }

    // when
    const result = checkIfSearchAround(searchAround)

    // then
    expect(result).toBe('oui')
  })

  it('should return non when is search everywhere', () => {
    const searchAround = {
      everywhere: true,
      place: false,
      user: false,
    }

    // when
    const result = checkIfSearchAround(searchAround)

    // then
    expect(result).toBe('non')
  })
})
