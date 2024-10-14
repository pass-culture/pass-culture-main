import { humanizeSiret } from '../utils'

describe('core | Venue | utils | humanizeSiret', () => {
  describe('when siret given is an empty string', () => {
    it('should return an empty string', () => {
      const siret = humanizeSiret('')
      expect(siret).toBe('')
    })
  })

  describe('when siret given is not a number', () => {
    it('should return a string with only numbers', () => {
      const siret = humanizeSiret('100F')
      expect(siret).toBe('100')
    })
  })

  describe('when siret given is a number', () => {
    it('should format siret string', () => {
      const siret = humanizeSiret('41816609600069')
      expect(siret).toBe('418 166 096 00069')
    })
  })
})
