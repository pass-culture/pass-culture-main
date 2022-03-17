import { unhumanizeSiret } from '../utils'

describe('core | Venue | utils | unhumanizeSiret', () => {
  describe('when siret given is an empty string', () => {
    it('should return an empty string', () => {
      const siret = unhumanizeSiret('')
      expect(siret).toBe('')
    })
  })

  describe('when siret given is not a number', () => {
    it('should return a string with only numbers', () => {
      const siret = unhumanizeSiret('100F')
      expect(siret).toBe('100')
    })
  })

  describe('when siret given containe whitespaces', () => {
    it('should remove whitespaces', () => {
      const siret = unhumanizeSiret('418 166 096 00069')
      expect(siret).toBe('41816609600069')
    })
  })
})
