import {
  formatSiret,
  getLocationInformationsFromSiret,
  getSiretInformations,
  validateSiretSize
} from '../selectSiretInformations'

describe('src | components | pages | Venue | siret | selectSiretInformations', () => {

  beforeEach(() => {
    fetch.resetMocks()
  })

  describe('formatSiret', () => {
    describe('when siret given is an empty string', () => {
      it('should return an empty string', () => {
        // given
        const siret = ''

        // when
        const formatedSiret = formatSiret(siret)

        // then
        expect(formatedSiret).toBe('')
      })
    })

    describe('when siret given is not a number', () => {
      it('should return a string with only numbers', () => {
        // given
        const siret = '100F'

        // when
        const formatedSiret = formatSiret(siret)

        // then
        expect(formatedSiret).toBe('100')
      })
    })

    describe('when siret given is a number', () => {
      it('should format siret string', () => {
        // given
        const siret = '41816609600069'

        // when
        const formatedSiret = formatSiret(siret)

        // then
        expect(formatedSiret).toBe('418 166 096 00069')
      })
    })
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

  describe('getLocationInformationsFromSiret', () => {
    describe('if siret provided is not valid', () => {
      it('should return ’SIRET invalide’', async () => {
        // given
        const siret = '12345678901234'
        fetch.mockResponseOnce(JSON.stringify({message:'no results found'}), { status: 404 })

        // when
        const errorMessage = await getLocationInformationsFromSiret(siret)

        // then
        expect(fetch.mock.calls.length).toBe(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(`https://entreprise.data.gouv.fr/api/sirene/v1/siret/${siret}`)
        expect(errorMessage).toStrictEqual({"error": "SIRET invalide"})
      })
    })

    describe('if siret provided is valid', () => {
      it('should return location values', async () => {
        // given
        const siret = '41816609600069'
        fetch.mockResponseOnce(JSON.stringify({
          etablissement : {
            l4_normalisee: '3 rue de la gare',
            libelle_commune: 'paris',
            latitude: 1.1,
            longitude: 1.1,
            l1_normalisee: 'nom du lieu',
            code_postal: '75000',
            siret: '41816609600069'
          }
        }))

        // when
        const locationValues = await getLocationInformationsFromSiret(siret)

        // then
        expect(fetch.mock.calls.length).toBe(1)
        expect(fetch.mock.calls[0][0]).toStrictEqual(`https://entreprise.data.gouv.fr/api/sirene/v1/siret/${siret}`)
        expect(locationValues).toStrictEqual({
          address: '3 rue de la gare',
          city: 'paris',
          latitude: 1.1,
          longitude: 1.1,
          name: 'nom du lieu',
          postalCode: '75000',
          siret: '41816609600069',
          sire: '41816609600069',
        })
      })
    })
  })

  describe('getSiretInformations', () => {
    describe('if not siret is provided', () => {
      it('should return empty location values', async () => {
        // given
        const siret = ''

        // when
        const locationValues = await getSiretInformations(siret)

        // then
        expect(fetch.mock.calls.length).toBe(0)
        expect(locationValues).toStrictEqual({
          values : {
            address: '',
            city: '',
            latitude: null,
            longitude: null,
            name: "",
            postalCode: '',
            sire: '',
            siret: '',
          }
        })
      })
    })
  })
})
