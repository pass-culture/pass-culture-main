import { getExpirationText } from '../getExpirationText'

describe('getExpirationText', () => {
  it("returns and empty strings if it's expiring in more than 7 days", () => {
    expect(getExpirationText(7)).not.toBe('')
    expect(getExpirationText(8)).toBe('')
  })

  it('returns the right number of days before expiration', () => {
    expect(getExpirationText(7)).toBe('Expire dans 7 jours')
    expect(getExpirationText(1)).toBe('Expire dans 1 jour')
  })

  it('returns "Aujourd\'hui" if it\'s expiring today', () => {
    expect(getExpirationText(0)).toBe("Expire aujourd'hui")
  })
})
