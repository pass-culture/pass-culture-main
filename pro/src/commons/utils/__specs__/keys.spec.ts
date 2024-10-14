import { getKey } from '../strings'

describe('getKeys', () => {
  it('should return a lowercase string without spaces', () => {
    expect(getKey('Petit test de%%_345')).toBe('petit-test-de%%_345')
  })
})
