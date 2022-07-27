import { unhumanizeSiren } from 'core/Offerers/utils'

import getSirenDataAdapter from '../getSirenDataAdapter'

describe('getSirenDataAdapter', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('when the SIREN does not exist', () => {
    it('test invalid siret response', async () => {
      // given
      const siren = '245474278'
      fetch.mockResponseOnce(JSON.stringify({ message: 'no results found' }), {
        status: 404,
      })

      // when
      const response = await getSirenDataAdapter(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe("Ce SIREN n'est pas reconnu")
      expect(response.payload).toStrictEqual({})
    })

    it('test unavailable service response', async () => {
      // given
      const siren = '345474278'
      fetch.mockResponseOnce(
        JSON.stringify({ message: 'service unavailable' }),
        { status: 503 }
      )

      // when
      const response = await getSirenDataAdapter(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(response.isOk).toBeFalsy()
      expect(response.message).toBe(
        'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
      )
      expect(response.payload).toStrictEqual({})
    })
  })

  describe('when the SIREN exists', () => {
    it('should return location values', async () => {
      // given
      const siren = '445474278'
      fetch.mockResponseOnce(
        JSON.stringify({
          unite_legale: {
            denomination: 'nom du lieu',
            siren: siren,
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
      const response = await getSirenDataAdapter(siren)

      // then
      expect(fetch.mock.calls).toHaveLength(1)
      expect(fetch.mock.calls[0][0]).toBe(
        `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
      )
      expect(response.isOk).toBeTruthy()
      expect(response.message).toBe(
        `Informations récupéré avec success pour le SIREN: ${unhumanizeSiren(
          siren
        )}`
      )
      expect(response.payload).toStrictEqual({
        values: {
          address: '3 rue de la gare',
          city: 'paris',
          latitude: 1.1,
          longitude: 1.1,
          name: 'nom du lieu',
          postalCode: '75000',
          siren: siren,
        },
      })
    })

    describe('when offerer name is not in normalized', () => {
      it('should use the declared name', async () => {
        // given
        const siren = '545474278'
        fetch.mockResponseOnce(
          JSON.stringify({
            unite_legale: {
              siren: siren,
              etablissement_siege: {
                geo_l4: '3 rue de la gare',
                libelle_commune: 'paris',
                latitude: 1.1,
                longitude: 1.1,
                enseigne_1: 'Nom déclaré du lieu',
                code_postal: '75000',
                siren: siren,
              },
            },
          })
        )

        // when
        const response = await getSirenDataAdapter(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toBe(
          `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
        )
        expect(response.isOk).toBeTruthy()
        expect(response.message).toBe(
          `Informations récupéré avec success pour le SIREN: ${unhumanizeSiren(
            siren
          )}`
        )
        expect(response.payload.values).toMatchObject({
          name: 'Nom déclaré du lieu',
        })
      })
    })

    describe('when offerer has no name', () => {
      it('should have use firstname and lastname', async () => {
        // given
        const siren = '645474278'
        fetch.mockResponseOnce(
          JSON.stringify({
            unite_legale: {
              siren: siren,
              prenom_1: 'John',
              nom: 'Do',
              etablissement_siege: {
                geo_l4: '3 rue de la gare',
                libelle_commune: 'paris',
                latitude: 1.1,
                longitude: 1.1,
                code_postal: '75000',
                siren: siren,
              },
            },
          })
        )

        // when
        const response = await getSirenDataAdapter(siren)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toBe(
          `https://entreprise.data.gouv.fr/api/sirene/v3/unites_legales/${siren}`
        )
        expect(response.isOk).toBeTruthy()
        expect(response.message).toBe(
          `Informations récupéré avec success pour le SIREN: ${unhumanizeSiren(
            siren
          )}`
        )
        expect(response.payload.values).toMatchObject({
          name: 'John Do',
        })
      })
    })
  })
})
