import { sirenUpdate } from '../decorators'

const sirenApiUrl = siren =>
  `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`

describe('sirenUpdate', () => {
  beforeEach(() => {
    fetch.mockResponse(
      JSON.stringify({
        address: null,
        city: null,
        name: null,
        postalCode: null,
        siren: '841166096',
      }),
      {
        status: 200,
      }
    )
  })

  describe('when the SIREN is not complete', () => {
    it('should not load SIREN information', () => {
      // Given
      const siren = '418'

      // When
      sirenUpdate(siren)

      // Then
      expect(fetch).not.toHaveBeenCalled()
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
    it('should load offerer details from API', () => {
      // Given
      const siren = '418166096'

      // When
      sirenUpdate(siren)

      // Then
      expect(fetch).toHaveBeenCalledWith(sirenApiUrl(siren))
    })

    it('should format the SIREN to the API standards', () => {
      // Given
      const siren = '418 166 096'

      // When
      sirenUpdate(siren)

      // Then
      expect(fetch).toHaveBeenCalledWith(sirenApiUrl('418166096'))
    })
  })

  it('should format the SIREN to exclude extra characters', () => {
    // Given
    const siren = '841 166 09616'

    // When
    sirenUpdate(siren)

    // Then
    expect(fetch).toHaveBeenCalledWith(sirenApiUrl('841166096'))
  })

  it('should return the result', async () => {
    // Given
    const siren = '841 166 096'

    // When
    const result = await sirenUpdate(siren)

    // Then
    expect(result).toStrictEqual({
      address: '',
      name: '',
      siren: siren,
      postalCode: '',
      city: '',
    })
  })
})
