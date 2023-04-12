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
})
