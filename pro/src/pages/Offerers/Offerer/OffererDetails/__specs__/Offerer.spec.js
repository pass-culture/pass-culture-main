import { Offerer } from '../Offerer'

describe('src | components | pages | OffererCreation | Offerer', () => {
  describe('constructor', () => {
    it('should instantiate Offerer object with default values', () => {
      // When
      const result = new Offerer()

      // Then
      expect(result).toMatchObject({
        id: undefined,
        siren: '',
        name: '',
        address: '',
        postalCode: '',
        city: '',
        bic: '',
        iban: '',
      })
    })

    it('should instantiate Offerer object with offerer values', () => {
      // Given
      const properties = {
        id: 'B3',
        postalCode: '75001',
        city: 'PARIS',
      }

      // When
      const result = new Offerer(properties)

      // Then
      expect(result).toMatchObject({
        id: 'B3',
        postalCode: '75001',
        city: 'PARIS',
      })
    })
  })

  describe('areBankInformationProvided', () => {
    describe('when offerer bic and iban exists', () => {
      it('should return true', () => {
        // given
        const offerer = {
          name: 'name',
          bic: 'bic',
          iban: 'iban',
        }
        const offererInstance = new Offerer(offerer, {})

        // then
        expect(offererInstance.areBankInformationProvided).toBe(true)
      })
    })

    describe('when offerer bic doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
          iban: 'iban',
        }
        const offererInstance = new Offerer(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided).toBe(false)
      })
    })

    describe('when offerer iban doesnt exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
          bic: 'bic',
        }
        const offererInstance = new Offerer(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided).toBe(false)
      })
    })

    describe('when neither offerer iban or bic exist', () => {
      it('should return false', () => {
        // given
        const offerer = {
          name: 'name',
        }
        const offererInstance = new Offerer(offerer, {})
        // when then
        expect(offererInstance.areBankInformationProvided).toBe(false)
      })
    })
  })
})
