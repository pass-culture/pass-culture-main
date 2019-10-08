import { OffererClass } from '../OffererClass'

describe('src | components | pages | Offerer | OffererClass', () => {
  describe('isIdOrNameDefined', () => {
    describe('when offerer id exists', () => {
      it('should return true', () => {
        // given
        const offerer = new OffererClass('id', '', 'bic', 'iban', {})

        // when then
        expect(offerer.isIdOrNameDefined()).toBe(true)
      })
    })

    describe('when offerer name exists', () => {
      it('should return true', () => {
        // given
        const offerer = new OffererClass('', 'name', 'bic', 'iban', {})

        // when then
        expect(offerer.isIdOrNameDefined()).toBe(true)
      })
    })

    describe('when neither id or name exists', () => {
      it('should return false', () => {
        // given
        const offerer = new OffererClass('', 'siren', '', 'address', 'bic', 'iban', {})

        // when then
        expect(offerer.isIdOrNameDefined()).toBe(false)
      })
    })
  })

  describe('areBankInformationProvided', () => {
    describe('when offerer bic and iban exists', () => {
      it('should return true', () => {
        // given
        const offerer = new OffererClass('id', 'siren', 'name', 'address', 'bic', 'iban', {})

        // when then
        expect(offerer.areBankInformationProvided()).toBe(true)
      })
    })

    describe('when offerer bic doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = new OffererClass('', 'siren', '', 'address', '', 'iban', {})

        // when then
        expect(offerer.areBankInformationProvided()).toBe(false)
      })
    })

    describe('when offerer iban doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = new OffererClass('', 'siren', '', 'address', 'bic', '', {})

        // when then
        expect(offerer.areBankInformationProvided()).toBe(false)
      })
    })

    describe('when neither offerer iban or bic exist', () => {
      it('should return false', () => {
        // given
        const offerer = new OffererClass('', 'siren', '', 'address', '', '', {})

        // when then
        expect(offerer.areBankInformationProvided()).toBe(false)
      })
    })
  })
})
