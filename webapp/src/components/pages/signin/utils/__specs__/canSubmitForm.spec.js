import canSubmitForm from '../canSubmitForm'

describe('src | components | pages | signin | canSubmitForm', () => {
  describe('when missing arguments', () => {
    it('should throw when missing arguments', () => {
      expect(() => {
        // when
        canSubmitForm()
      }).toThrow('canSubmitForm: Missing arguments')
    })
  })

  describe('when form is dirty', () => {
    describe('when form has no submit errors', () => {
      describe('when form has no validation errors', () => {
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
          expect(result).toStrictEqual(true)
        })
      })

      describe('when form has some validation errors', () => {
        it('should return false', () => {
          // given
          const value = {
            hasSubmitErrors: false,
            hasValidationErrors: true,
            pristine: false,
          }
          // when
          const result = canSubmitForm(value)

          // then
          expect(result).toStrictEqual(false)
        })
      })
    })
  })

  describe('when form is dirty since last submit', () => {
    describe('when form has submit errors', () => {
      describe('when form has no validation errors', () => {
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
          expect(result).toStrictEqual(true)
        })
      })

      describe('when form has some validation errors', () => {
        it('should return true', () => {
          // given
          const value = {
            dirtySinceLastSubmit: true,
            hasSubmitErrors: true,
            hasValidationErrors: true,
          }

          // when
          const result = canSubmitForm(value)

          // then
          expect(result).toStrictEqual(false)
        })
      })
    })
  })
})
