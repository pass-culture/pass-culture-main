import {
  getSiretInformations,
  validateSiretSize,
} from '../selectSiretInformations'

describe('src | components | pages | Venue | siret | selectSiretInformations', () => {
  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('validateSiretSize', () => {
    describe('when siret lenght is smaller than 14 characters', () => {
      it('should return ’SIRET trop court’', () => {
        // given
        const siret = '1234'

        // when
        const errorMessage = validateSiretSize(siret)

        // then
        expect(errorMessage).toBe('SIRET trop court')
      })
    })

    describe('when siret lenght is greater than 14 characters', () => {
      it('should return ’SIRET trop long’', () => {
        // given
        const siret = '123456789123456789'

        // when
        const errorMessage = validateSiretSize(siret)

        // then
        expect(errorMessage).toBe('SIRET trop long')
      })
    })

    describe('when siret lenght is 14 characters', () => {
      it('should return no error', () => {
        // given
        const siret = '12345678912345'

        // when
        const errorMessage = validateSiretSize(siret)

        // then
        expect(errorMessage).toBe('')
      })
    })
  })

  describe('getLocationInformationsFromSiret', () => {})

  describe('getSiretInformations', () => {
    describe('if not siret is provided', () => {
      it('should return empty location values', async () => {
        // given
        const siret = ''

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(0)
        expect(locationValues).toStrictEqual({
          values: {
            address: '',
            city: '',
            latitude: null,
            longitude: null,
            name: '',
            postalCode: '',
            sire: '',
            siret: '',
          },
        })
      })
    })

    describe('if siret provided is not valid', () => {
      it('should return ’SIRET invalide’', async () => {
        // given
        const siret = '12345678901234'
        fetch.mockResponseOnce(
          JSON.stringify({ message: 'no results found' }),
          { status: 404 }
        )

        // when
        const errorMessage = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
        )
        expect(errorMessage).toStrictEqual({
          values: { error: 'SIRET invalide' },
        })
      })
    })

    describe('if siret provided is valid', () => {
      it('should return location values with enseigne as name if provided', async () => {
        // given
        const siret = '41816609600069'
        fetch.mockResponseOnce(
          JSON.stringify({
            etablissement: {
              geo_l4: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              enseigne_1: 'nom du lieu',
              code_postal: '75000',
              siret: '41816609600069',
            },
          })
        )

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
        )
        expect(locationValues).toStrictEqual({
          values: {
            address: '3 rue de la gare',
            city: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            name: 'nom du lieu',
            postalCode: '75000',
            siret: '41816609600069',
            sire: '41816609600069',
          },
        })
      })

      it('should return location values with unité légale denomination as name if no enseigne is provided', async () => {
        // given
        const siret = '41816609600070'
        fetch.mockResponseOnce(
          JSON.stringify({
            etablissement: {
              geo_l4: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              enseigne_1: null,
              code_postal: '75000',
              siret: '41816609600070',
              unite_legale: {
                denomination: 'headquarters name',
              },
            },
          })
        )

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
        )
        expect(locationValues).toStrictEqual({
          values: {
            address: '3 rue de la gare',
            city: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            name: 'headquarters name',
            postalCode: '75000',
            siret: '41816609600070',
            sire: '41816609600070',
          },
        })
      })

      it('should return location values with empty string as name if no enseigne and denomination are provided', async () => {
        // given
        const siret = '41816609600071'
        fetch.mockResponseOnce(
          JSON.stringify({
            etablissement: {
              geo_l4: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              enseigne_1: null,
              code_postal: '75000',
              siret: '41816609600071',
              unite_legale: {
                denomination: null,
              },
            },
          })
        )

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(
          `https://entreprise.data.gouv.fr/api/sirene/v3/etablissements/${siret}`
        )
        expect(locationValues).toStrictEqual({
          values: {
            address: '3 rue de la gare',
            city: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            name: '',
            postalCode: '75000',
            siret: '41816609600071',
            sire: '41816609600071',
          },
        })
      })

      it('should cache request', async () => {
        // given
        const siret = '41816609600072'
        fetch.mockResponseOnce(
          JSON.stringify({
            etablissement: {
              geo_l4: '3 rue de la gare',
              libelle_commune: 'paris',
              latitude: 1.1,
              longitude: 1.1,
              enseigne_1: 'nom du lieu',
              code_postal: '75000',
              siret: '41816609600072',
            },
          })
        )
        await getSiretInformations(siret)
        await getSiretInformations('41816609600073')
        fetch.resetMocks()

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls).toHaveLength(0)
        expect(locationValues).toStrictEqual({
          values: {
            address: '3 rue de la gare',
            city: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            name: 'nom du lieu',
            postalCode: '75000',
            siret: '41816609600072',
            sire: '41816609600072',
          },
        })
      })
    })
  })
})
