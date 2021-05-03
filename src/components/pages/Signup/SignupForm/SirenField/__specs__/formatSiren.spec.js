import formatSiren from '../formatSiren'

describe('src | components | pages | OffererCreation | siren | formatSiren', () => {
  describe('when siren is undefined', () => {
    it('should return an empty string', () => {
      // given
      const siren = undefined

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('')
    })
  })

  describe('when siren given is an empty string', () => {
    it('should return an empty string', () => {
      // given
      const siren = ''

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('')
    })
  })

  describe('when siren given is a letter', () => {
    it('should return an empty string', () => {
      // given
      const siren = 'a'

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('')
    })
  })

  describe('when siren given is not a number', () => {
    it('should return a string with only numbers', () => {
      // given
      const siren = '100F'

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('100')
    })
  })

  describe('when value given is a valid SIRET', () => {
    it('returns a formatted siren', () => {
      // given
      const siren = '41816609600069'

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('418166096')
    })
  })

  describe('when value given is a valid SIREN', () => {
    it('should ignore whitespaces', () => {
      // given
      const siren = '418    166 096'

      // when
      const formatedSiren = formatSiren(siren)

      // then
      expect(formatedSiren).toBe('418166096')
    })
  })
})
