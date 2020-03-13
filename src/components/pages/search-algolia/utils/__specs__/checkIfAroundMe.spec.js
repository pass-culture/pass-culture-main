import { checkIfAroundMe } from '../checkIfAroundMe'

describe('utils | checkIfAroundMe', () => {
  it('should return oui when is search around me', () => {
    const criteria = true

    // when
    const result = checkIfAroundMe(criteria)

    // then
    expect(result).toBe('oui')
  })

  it('should return non when is search around me', () => {
    const criteria = false

    // when
    const result = checkIfAroundMe(criteria)

    // then
    expect(result).toBe('non')
  })
})
