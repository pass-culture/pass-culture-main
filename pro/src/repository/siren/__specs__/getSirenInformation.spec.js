import { getSirenInformation } from '../getSirenInformation'

describe('getSirenInformations', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('when the SIREN does not exist', () => {
    it('should return ’SIREN invalide’', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      const errorMessage = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(errorMessage).toStrictEqual({ error: 'SIREN invalide' })
    })

    it('should return ’Service indisponible’ when API siren does not respond', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(
        JSON.stringify({ message: 'service unavailable' }),
        { status: 503 }
      )

      // when
      const errorMessage = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(errorMessage).toStrictEqual({ error: 'Service indisponible' })
    })
  })

  describe('when the SIREN exists', () => {
    it('should return location values', async () => {
      // given
      const siren = '418166096'
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
      const locationValues = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(locationValues).toStrictEqual({
        address: '3 rue de la gare',
        city: 'paris',
        latitude: 1.1,
        longitude: 1.1,
        name: 'nom du lieu',
        postalCode: '75000',
        siren: '418166096',
      })
    })

    describe('when offerer name is not in normalized', () => {
      it('should use the declared name', async () => {
        // given
        const siren = '418166096'
        fetch.mockResponseOnce(
          JSON.stringify({
            unite_legale: {
              siren: '418166096',
              etablissement_siege: {
                geo_l4: '3 rue de la gare',
                libelle_commune: 'paris',
                latitude: 1.1,
                longitude: 1.1,
                enseigne_1: 'Nom déclaré du lieu',
                code_postal: '75000',
                siren: '418166096',
              },
            },
          })
        )

        // when
        const locationValues = await getSirenInformation(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toBe(
          `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
        )
        expect(locationValues).toMatchObject({
          name: 'Nom déclaré du lieu',
        })
      })
    })

    describe('when offerer has no name', () => {
      it('should have use firstname and lastname', async () => {
        // given
        const siren = '418166096'
        fetch.mockResponseOnce(
          JSON.stringify({
            unite_legale: {
              siren: '418166096',
              prenom_1: 'John',
              nom: 'Do',
              etablissement_siege: {
                geo_l4: '3 rue de la gare',
                libelle_commune: 'paris',
                latitude: 1.1,
                longitude: 1.1,
                code_postal: '75000',
                siren: '418166096',
              },
            },
          })
        )

        // when
        const locationValues = await getSirenInformation(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toBe(
          `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
        )
        expect(locationValues).toMatchObject({
          name: 'John Do',
        })
      })
    })
  })
})
