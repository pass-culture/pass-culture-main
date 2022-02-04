import formatSiren from '../formatSiren'

describe('src | components | pages | OffererCreation | siren | formatSiren', () => {
  describe('when siren is undefined', () => {
    it('should return an empty string', () => {
      // given
      const siren = undefined

      // when
      const formatedSiret = formatSiren(siren)

      // then
      expect(formatedSiret).toBe('')
    })
  })

  describe('when siren given is an empty string', () => {
    it('should return an empty string', () => {
      // given
      const siren = ''

      // when
      const formatedSiret = formatSiren(siren)

      // then
      expect(formatedSiret).toBe('')
    })
  })

  describe('when siren given is not a number', () => {
    it('should return a string with only numbers', () => {
      // given
      const siren = '100F'

      // when
      const formatedSiret = formatSiren(siren)

      // then
      expect(formatedSiret).toBe('100')
    })
  })

  describe('when value given is a valid SIRET', () => {
    it('returns a formatted siren', () => {
      // given
      const siren = '41816609600069'

      // when
      const formatedSiret = formatSiren(siren)

      // then
      expect(formatedSiret).toBe('418166096')
    })
  })

  describe('when value given is a valid SIREN', () => {
    it('should ignore whitespaces', () => {
      // given
      const siren = '418    166 096'

      // when
      const formatedSiret = formatSiren(siren)

      // then
      expect(formatedSiret).toBe('418166096')
    })
  })
})
