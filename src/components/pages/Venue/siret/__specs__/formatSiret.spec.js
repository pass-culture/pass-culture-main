import { formatSiret } from '../formatSiret'

describe('src | components | pages | Venue | siret | formatSiret', () => {
  describe('when siret given is an empty string', () => {
    it('should return an empty string', () => {
      // given
      const siret = ''

      // when
      const formatedSiret = formatSiret(siret)

      // then
      expect(formatedSiret).toBe('')
    })
  })

  describe('when siret given is not a number', () => {
    it('should return a string with only numbers', () => {
      // given
      const siret = '100F'

      // when
      const formatedSiret = formatSiret(siret)

      // then
      expect(formatedSiret).toBe('100')
    })
  })

  describe('when siret given is a number', () => {
    it('should format siret string', () => {
      // given
      const siret = '41816609600069'

      // when
      const formatedSiret = formatSiret(siret)

      // then
      expect(formatedSiret).toBe('418 166 096 00069')
    })
  })
})
