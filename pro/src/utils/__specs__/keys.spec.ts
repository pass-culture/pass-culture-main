import { getKey } from '../keys'

describe('getKeys', () => {
  it('should return a lowercase string without spaces', () => {
    expect(getKey('Petit test de%%_345')).toBe('petittestde%%_345')
  })
})
