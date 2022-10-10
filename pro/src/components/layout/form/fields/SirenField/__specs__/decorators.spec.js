import { api } from 'apiClient/api'

import { sirenUpdate } from '../decorators'

describe('sirenUpdate', () => {
  beforeEach(() => {
    jest.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'nom du lieu',
      siren: '841166096',
      address: {
        street: '3 rue de la gare',
        city: 'paris',
        postalCode: '75000',
      },
    })
  })

  describe('when the SIREN is not complete', () => {
    it('should not load SIREN information', () => {
      // Given
      const siren = '418'

      // When
      sirenUpdate(siren)

      // Then
      expect(api.getSirenInfo).not.toHaveBeenCalled()
    })

    it('should return empty information', async () => {
      // Given
      const siren = '418 71'

      // When
      const result = await sirenUpdate(siren)

      // Then
      expect(result).toStrictEqual({
        address: '',
        city: '',
        name: '',
        postalCode: '',
        siren: '418 71',
      })
    })
  })

  describe('when the SIREN has the required 9 numbers', () => {
    it('should load offerer details from API', async () => {
      // Given
      const siren = '418166096'

      // When
      await sirenUpdate(siren)

      // Then
      expect(api.getSirenInfo).toHaveBeenCalledWith(siren)
    })

    it('should format the SIREN to the API standards', async () => {
      // Given
      const siren = '418 166 096'

      // When
      await sirenUpdate(siren)

      // Then
      expect(api.getSirenInfo).toHaveBeenCalledWith(
        expect.stringContaining('418166096')
      )
    })
  })

  it('should format the SIREN to exclude extra characters', async () => {
    // Given
    const siren = '841 166 09616'

    // When
    await sirenUpdate(siren)

    // Then
    expect(api.getSirenInfo).toHaveBeenCalledWith(
      expect.stringContaining('841166096')
    )
  })

  it('should return the result', async () => {
    // Given
    const siren = '841 166 096'

    // When
    const result = await sirenUpdate(siren)

    // Then
    expect(result).toStrictEqual({
      address: '3 rue de la gare',
      name: 'nom du lieu',
      siren: '841166096',
      postalCode: '75000',
      city: 'paris',
    })
  })
})
