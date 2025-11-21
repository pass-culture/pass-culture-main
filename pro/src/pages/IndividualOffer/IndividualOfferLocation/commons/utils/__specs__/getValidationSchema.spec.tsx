import { OFFER_LOCATION } from '../../../../commons/constants'
import { makeLocationFormValues } from '../../__mocks__/makeLocationFormValues'
import type { LocationFormValues, NullableIfNonBoolean } from '../../types'
import { getValidationSchema } from '../getValidationSchema'

const VALID_URL = 'https://passculture.app'
const INVALID_URL = 'invalid-url'
const VALID_COORDS = '1.2345, 6.7890'
const INVALID_COORDS = 'invalid-coords'

describe('getValidationSchema', () => {
  const defaultFormValues: NullableIfNonBoolean<LocationFormValues> =
    makeLocationFormValues({})

  const baseAddress = makeLocationFormValues({
    location: { offerLocation: OFFER_LOCATION.OTHER_ADDRESS },
  }).location

  const buildWithAddress = (overrides: Record<string, unknown>) =>
    makeLocationFormValues({
      location: { ...baseAddress, ...overrides },
    })

  describe('when isDigital is true', () => {
    const schema = getValidationSchema({ isDigital: true })

    it('should require url', async () => {
      await expect(schema.validateAt('url', defaultFormValues)).rejects.toThrow(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )
    })

    it('should require a valid url', async () => {
      await expect(
        schema.validateAt('url', {
          ...defaultFormValues,
          url: INVALID_URL,
        })
      ).rejects.toThrow(
        'Veuillez renseigner une URL valide. Ex : https://exemple.com'
      )

      await expect(
        schema.validateAt('url', {
          ...defaultFormValues,
          url: VALID_URL,
        })
      ).resolves.toBe(VALID_URL)
    })
  })

  describe('when isDigital is false', () => {
    const schema = getValidationSchema({ isDigital: false })

    it('should require location.offerLocation when address object present', async () => {
      const values = buildWithAddress({ offerLocation: null })

      await expect(
        schema.validateAt('location.offerLocation', values)
      ).rejects.toThrow('Veuillez sélectionner un choix')
    })

    it('should not require url when offline (and accept any format)', async () => {
      await expect(
        schema.validateAt('url', defaultFormValues)
      ).resolves.toBeNull()
      await expect(
        schema.validateAt('url', { ...defaultFormValues, url: INVALID_URL })
      ).resolves.toBe(INVALID_URL)
    })

    it('should accept a valid url', async () => {
      await expect(
        schema.validateAt('url', {
          ...defaultFormValues,
          url: VALID_URL,
        })
      ).resolves.toBe(VALID_URL)
    })

    describe('when offerLocation is OTHER_ADDRESS', () => {
      const formValuesWithOtherAddress = buildWithAddress({})

      it('should require city, postalCode, and street', async () => {
        await expect(
          schema.validateAt('location.city', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner une ville')
        await expect(
          schema.validateAt('location.postalCode', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner un code postal')
        await expect(
          schema.validateAt('location.street', formValuesWithOtherAddress)
        ).rejects.toThrow('Veuillez renseigner une adresse postale')
      })

      it('should require a 5-digit postal code', async () => {
        await expect(
          schema.validateAt(
            'location.postalCode',
            buildWithAddress({ postalCode: '1234' })
          )
        ).rejects.toThrow('Veuillez renseigner un code postal valide')
        await expect(
          schema.validateAt(
            'location.postalCode',
            buildWithAddress({ postalCode: '123456' })
          )
        ).rejects.toThrow('Veuillez renseigner un code postal valide')
      })

      describe('and isManualEdition is false', () => {
        it('should require addressAutocomplete', async () => {
          const values = buildWithAddress({ isManualEdition: false })
          await expect(
            schema.validateAt('location.addressAutocomplete', values)
          ).rejects.toThrow(
            'Veuillez sélectionner une adresse parmi les suggestions'
          )
        })
      })

      describe('and isManualEdition is true', () => {
        const formValuesWithManualAddress = buildWithAddress({
          isManualEdition: true,
        })

        it('should require coords', async () => {
          await expect(
            schema.validateAt('location.coords', formValuesWithManualAddress)
          ).rejects.toThrow('Veuillez renseigner les coordonnées GPS')
        })

        it('should require valid coords format', async () => {
          const invalidCoordsValues = buildWithAddress({
            isManualEdition: true,
            coords: INVALID_COORDS,
          })

          await expect(
            schema.validateAt('location.coords', invalidCoordsValues)
          ).rejects.toThrow('Veuillez respecter le format attendu')
        })

        it('should accept valid coords', async () => {
          const validCoordsValues = buildWithAddress({
            isManualEdition: true,
            coords: VALID_COORDS,
          })

          await expect(
            schema.validateAt('location.coords', validCoordsValues)
          ).resolves.toBe(VALID_COORDS)
        })
      })
    })

    it('should transform isVenueLocation to true when offerLocation is venue id', async () => {
      const values = buildWithAddress({
        offerLocation: '123',
        isVenueLocation: false,
        street: '1 rue test',
        city: 'Paris',
        postalCode: '75001',
        latitude: '1',
        longitude: '2',
      })

      const result = await schema.validate({ ...values })

      expect(result.location?.isVenueLocation).toBe(true)
    })

    it('should transform isVenueLocation to false when offerLocation is OTHER_ADDRESS', async () => {
      const values = buildWithAddress({
        offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
        isVenueLocation: true,
        street: '1 rue test',
        city: 'Paris',
        postalCode: '75001',
        latitude: '1',
        longitude: '2',
        addressAutocomplete: '1 rue test 75001 Paris',
      })

      const result = await schema.validate({ ...values })

      expect(result.location?.isVenueLocation).toBe(false)
    })
  })
})
