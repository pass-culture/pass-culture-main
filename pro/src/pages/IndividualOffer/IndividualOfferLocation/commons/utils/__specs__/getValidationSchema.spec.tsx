import { OFFER_LOCATION } from '../../../../commons/constants'
import { DEFAULT_LOCATION_FORM_INITIAL_VALUES } from '../../constants'
import { getValidationSchema } from '../getValidationSchema'

const VALID_URL = 'https://passculture.app'
const INVALID_URL = 'invalid-url'
const VALID_COORDS = '1.2345, 6.7890'
const INVALID_COORDS = 'invalid-coords'

describe('getValidationSchema', () => {
  describe('when isOfferSubcategoryOnline is true', () => {
    const schema = getValidationSchema({ isOfferSubcategoryOnline: true })

    it('should require url', async () => {
      await expect(
        schema.validateAt('url', DEFAULT_LOCATION_FORM_INITIAL_VALUES)
      ).rejects.toThrow(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )
    })

    it('should require a valid url', async () => {
      await expect(
        schema.validateAt('url', {
          ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
          url: INVALID_URL,
        })
      ).rejects.toThrow(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )

      await expect(
        schema.validateAt('url', {
          ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
          url: VALID_URL,
        })
      ).resolves.toBe(VALID_URL)
    })
  })

  describe('when isOfferSubcategoryOnline is false', () => {
    const schema = getValidationSchema({ isOfferSubcategoryOnline: false })

    it('should require offerLocation', async () => {
      const call = () =>
        schema.validateAt('offerLocation', DEFAULT_LOCATION_FORM_INITIAL_VALUES)

      await expect(call).rejects.toThrow('Veuillez sélectionner un choix')
    })

    it('should not require url when offline (and accept any format)', async () => {
      await expect(
        schema.validateAt('url', DEFAULT_LOCATION_FORM_INITIAL_VALUES)
      ).resolves.toBeNull()

      await expect(
        schema.validateAt('url', {
          ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
          url: INVALID_URL,
        })
      ).resolves.toBe(INVALID_URL)
    })

    it('should accept a valid url', async () => {
      await expect(
        schema.validateAt('url', {
          ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
          url: VALID_URL,
        })
      ).resolves.toBe(VALID_URL)
    })

    describe('when offerLocation is OTHER_ADDRESS', () => {
      const formValuesWithOtherAddress = {
        ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
        offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
      }

      it('should require city, postalCode, and street', async () => {
        await expect(
          schema.validateAt('city', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner une ville')
        await expect(
          schema.validateAt('postalCode', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner un code postal')
        await expect(
          schema.validateAt('street', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner une adresse postale')
      })

      it('should require a 5-digit postal code', async () => {
        await expect(
          schema.validateAt('postalCode', {
            ...formValuesWithOtherAddress,
            postalCode: '1234',
          })
        ).rejects.toThrow('Veuillez renseigner un code postal valide')
        await expect(
          schema.validateAt('postalCode', {
            ...formValuesWithOtherAddress,
            postalCode: '123456',
          })
        ).rejects.toThrow('Veuillez renseigner un code postal valide')
      })

      describe('and isManualEdition is false', () => {
        it('should require addressAutocomplete', async () => {
          await expect(
            schema.validateAt('addressAutocomplete', {
              ...formValuesWithOtherAddress,
              isManualEdition: false,
            })
          ).rejects.toThrow(
            'Veuillez sélectionner une adresse parmi les suggestions'
          )
        })
      })

      describe('and isManualEdition is true', () => {
        const formValuesWithManualAddress = {
          ...formValuesWithOtherAddress,
          isManualEdition: true,
        }

        it('should require coords', async () => {
          await expect(
            schema.validateAt('coords', formValuesWithManualAddress)
          ).rejects.toThrow('Veuillez renseigner les coordonnées GPS')
        })

        it('should require valid coords format', async () => {
          await expect(
            schema.validateAt('coords', {
              ...formValuesWithManualAddress,
              coords: INVALID_COORDS,
            })
          ).rejects.toThrow('Veuillez respecter le format attendu')
        })

        it('should accept valid coords', async () => {
          await expect(
            schema.validateAt('coords', {
              ...formValuesWithManualAddress,
              coords: VALID_COORDS,
            })
          ).resolves.toBe(VALID_COORDS)
        })
      })
    })

    describe('when offerLocation is not OTHER_ADDRESS', () => {
      const formValuesWithVenue = {
        ...DEFAULT_LOCATION_FORM_INITIAL_VALUES,
        offerLocation: 'some-venue-id',
      }

      it('should not require address fields', async () => {
        const isValid = await schema.isValid({
          ...formValuesWithVenue,
          url: VALID_URL,
        })
        expect(isValid).toBe(true)
      })
    })
  })
})
