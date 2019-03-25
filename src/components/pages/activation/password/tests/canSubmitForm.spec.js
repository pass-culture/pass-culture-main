import canSubmitForm from '../canSubmitForm'

// FIXME: add missing tests
describe('src | components | pages | activation | tests | canSubmitForm', () => {
    it('it throw cause missing arguments', () => {
      expect(() => {
        // when
        canSubmitForm()
      }).toThrow()
    })

    it('should return true', () => {
      // given
      const value = {
        hasSubmitErrors: false,
        hasValidationErrors: false,
        pristine: false,
      }
      // when
      const result = canSubmitForm(value)

      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })

    it('should return true', () => {
      // given
      const value = {
        dirtySinceLastSubmit: true,
        hasSubmitErrors: true,
        hasValidationErrors: false,
      }

      // when
      const result = canSubmitForm(value)

      // then
      const expected = true
      expect(result).toStrictEqual(expected)
    })
})
