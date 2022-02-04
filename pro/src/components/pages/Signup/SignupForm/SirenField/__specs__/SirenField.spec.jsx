import { existsInINSEERegistry } from '../SirenField'

describe('src | components | SirenField', () => {
  describe('existsInINSEERegistry', () => {
    beforeEach(() => {
      fetch.resetMocks()
    })

    it('should call the INSEE API with the formatted SIREN', async () => {
      // given
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })
      const siren = '245 474 278'

      // when
      await existsInINSEERegistry(siren)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/245474278`
      )
    })

    it('should not return an error message when SIREN exists in INSEE registry', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(
        JSON.stringify({
          unite_legale: {
            denomination: 'nom du lieu',
            siren: '418166096',
            etablissement_siege: {
              geo_l4: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              code_postal: '75000',
            },
          },
        })
      )

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBeUndefined()
    })

    it('should return an error message when SIREN does not exist in INSEE registry', async () => {
      // given
      const siren = '245474279'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      const errorMessage = await existsInINSEERegistry(siren)

      // then
      expect(errorMessage).toBe("Ce SIREN n'est pas reconnu")
    })

    it('should check once for same SIREN called in INSEE registery', async () => {
      // given
      const siren = '245474280'
      fetch.mockResponse(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      await existsInINSEERegistry(siren)
      await existsInINSEERegistry(siren)

      // then
      expect(fetch).toHaveBeenCalledTimes(1)
      expect(fetch).toHaveBeenCalledWith(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/245474280`
      )
    })
  })
})
