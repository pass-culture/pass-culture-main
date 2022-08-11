import { sirenUpdate } from '../decorators'

describe('sirenUpdate', () => {
  beforeEach(() => {
    jest.spyOn(window, 'fetch').mockResolvedValueOnce({
      ok: true,
      status: 200,
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
      json: () =>
        Promise.resolve({
          name: 'nom du lieu',
          siren: '841166096',
          address: {
            street: '3 rue de la gare',
            city: 'paris',
            postalCode: '75000',
          },
        }),
    })
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
    it('should load offerer details from API', async () => {
      // Given
      const siren = '418166096'

      // When
      await sirenUpdate(siren)

      // Then
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sirene/siren/${siren}`),
        expect.anything()
      )
    })

    it('should format the SIREN to the API standards', async () => {
      // Given
      const siren = '418 166 096'

      // When
      await sirenUpdate(siren)

      // Then
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/sirene/siren/418166096'),
        expect.anything()
      )
    })
  })

  it('should format the SIREN to exclude extra characters', async () => {
    // Given
    const siren = '841 166 09616'

    // When
    await sirenUpdate(siren)

    // Then
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/sirene/siren/841166096'),
      expect.anything()
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
