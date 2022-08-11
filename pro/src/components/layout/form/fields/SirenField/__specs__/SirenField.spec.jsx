import { existsInINSEERegistry } from '../validate'

describe('components | SirenField', () => {
  describe('existsInINSEERegistry', () => {
    beforeEach(() => {
      fetch.resetMocks()
    })

    it('should call the INSEE API with the formatted SIREN', async () => {
      // given
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })
      const siren = '245474278'
      const humanSiren = '245 474 278'

      // when
      await existsInINSEERegistry(humanSiren)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sirene/siren/${siren}`),
        expect.anything()
      )
    })

    it('should not return an error message when SIREN exists in INSEE registry', async () => {
      // given
      const siren = '345474278'
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

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBeUndefined()
    })

    it('should return an error message when the unite_legal has anonymous data', async () => {
      // given
      const siren = '495474278'

      jest.spyOn(window, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: [
              'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles',
            ],
          }),
      })

      // when
      const errorMessage = await existsInINSEERegistry(siren)
      // then
      expect(errorMessage).toBe(
        'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles'
      )
    })

    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siren = '445474278'
      jest.spyOn(window, 'fetch').mockResolvedValue({
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.resolve({
            global: ["Ce SIREN ou SIRET n'existe pas."],
          }),
      })

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBe("Ce SIREN ou SIRET n'existe pas.")
    })

    it('should check once for same SIREN called in INSEE registery', async () => {
      // given
      const siren = '645474278'
      jest.spyOn(window, 'fetch').mockRejectedValueOnce({
        status: 400,
        headers: new Headers({
          'Content-Type': 'application/json',
        }),
        json: () =>
          Promise.reject({
            global: ['no results found'],
          }),
      })

      // when
      await existsInINSEERegistry(siren)
      await existsInINSEERegistry(siren)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/sirene/siren/${siren}`),
        expect.anything()
      )
    })
  })
})
