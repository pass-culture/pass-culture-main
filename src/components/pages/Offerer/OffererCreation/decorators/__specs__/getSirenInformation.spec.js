import getSirenInformation from '../getSirenInformation'

describe('getSirenInformations', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('when the SIREN does not exist', () => {
    it('should return ’SIREN invalide’', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), { status: 404 })

      // when
      const errorMessage = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toStrictEqual(
        `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`
      )
      expect(errorMessage).toStrictEqual({ error: 'SIREN invalide' })
    })

    it('should return ’Service indisponible’ when API siren does not respond', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(JSON.stringify({ message: 'service unavailable' }), { status: 503 })

      // when
      const errorMessage = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toStrictEqual(
        `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`
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
          siege_social: {
            l4_normalisee: '3 rue de la gare',
            libelle_commune: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            l1_normalisee: 'nom du lieu',
            code_postal: '75000',
            siren: '418166096',
          },
        })
      )

      // when
      const locationValues = await getSirenInformation(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toStrictEqual(
        `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`
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

    describe('when offerer name is not in l1_normalisee', () => {
      it('should use the declared name', async () => {
        // given
        const siren = '418166096'
        fetch.mockResponseOnce(
          JSON.stringify({
            siege_social: {
              l4_normalisee: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              l1_declaree: 'Nom déclaré du lieu',
              code_postal: '75000',
              siren: '418166096',
            },
          })
        )

        // when
        const locationValues = await getSirenInformation(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`
        )
        expect(locationValues).toMatchObject({
          name: 'Nom déclaré du lieu',
        })
      })
    })

    describe('when offerer has no name', () => {
      it('should have an empty name', async () => {
        // given
        const siren = '418166096'
        fetch.mockResponseOnce(
          JSON.stringify({
            siege_social: {
              l4_normalisee: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              code_postal: '75000',
              siren: '418166096',
            },
          })
        )

        // when
        const locationValues = await getSirenInformation(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v1/siren/${siren}`
        )
        expect(locationValues).toMatchObject({
          name: '',
        })
      })
    })
  })
})
