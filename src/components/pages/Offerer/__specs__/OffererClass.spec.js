import { OffererClass } from '../OffererClass'

describe('src | components | pages | Offerer | OffererClass', () => {
  describe('isIdOrNameDefined', () => {
    describe('when offerer id exists', () => {
      it('should return true', () => {
        // given
        const offerer = {
          id: 'id',
          bic: 'bic',
          iban: 'iban',
        }
        const offererInstance = new OffererClass(offerer, {})

        // when then
        expect(offererInstance.isIdOrNameDefined()).toBe(true)
      })
    })

    describe('when offerer name exists', () => {
      it('should return true', () => {
        // given
        const offerer = {
          name: 'name',
          bic: 'bic',
          iban: 'iban',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.isIdOrNameDefined()).toBe(true)
      })
    })

    describe('when neither id or name exists', () => {
      it('should return false', () => {
        // given
        const offerer = {
          bic: 'bic',
          iban: 'iban',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.isIdOrNameDefined()).toBe(false)
      })
    })
  })

  describe('areBankInformationProvided', () => {
    describe('when offerer bic and iban exists', () => {
      it('should return true', () => {
        const offerer = {
          name: 'name',
          bic: 'bic',
          iban: 'iban',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided()).toBe(true)
      })
    })

    describe('when offerer bic doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
          iban: 'iban',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided()).toBe(false)
      })
    })

    describe('when offerer iban doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
          bic: 'bic',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided()).toBe(false)
      })
    })

    describe('when neither offerer iban or bic exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
        }
        const offererInstance = new OffererClass(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided()).toBe(false)
      })
    })
  })
})
