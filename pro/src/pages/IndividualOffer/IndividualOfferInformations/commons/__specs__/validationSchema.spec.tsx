import { WithdrawalTypeEnum } from '@/apiClient/v1'

import type { UsefulInformationFormValues } from '../types'
import { getValidationSchema } from '../validationSchema'

describe('getValidationSchema', () => {
  describe.each([
    { isNewOfferCreationFlowFeatureActive: false },
    { isNewOfferCreationFlowFeatureActive: true },
  ])(
    'with isNewOfferCreationFlowFeatureActive = $isNewOfferCreationFlowFeatureActive (both)',
    ({ isNewOfferCreationFlowFeatureActive }) => {
      const baseParams = {
        isOfferOnline: false,
        isNewOfferCreationFlowFeatureActive,
      }

      const validInformationFormValuesBase: UsefulInformationFormValues =
        Object.assign(
          {
            locationLabel: 'label',
            offerLocation: 'location',
            addressAutocomplete: 'autocomplete',
            street: 'street',
            postalCode: '93160',
            city: 'city',
          },
          isNewOfferCreationFlowFeatureActive
            ? {}
            : {
                accessibility: {
                  mental: false,
                  audio: false,
                  visual: false,
                  motor: false,
                  none: true,
                },
              }
        )

      describe('should validate withdrawalType correctly', () => {
        it('should validate withdrawalType correctly', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: ['withdrawalType'],
          })

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
            })
          ).resolves.toBeTruthy()

          await expect(
            schema.validate({ ...validInformationFormValuesBase })
          ).rejects.toThrow('Veuillez sélectionner l’une de ces options')
        })

        it('should validate withdrawalDelay correctly', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: ['withdrawalDelay'],
          })

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
              withdrawalDelay: 'Some delay',
            })
          ).resolves.toBeTruthy()

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
              withdrawalDelay: '',
            })
          ).rejects.toThrow('Vous devez choisir l’une des options ci-dessus')
        })

        it('should validate bookingContact correctly', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: ['bookingContact'],
          })
          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              bookingContact: 'valid@example.com',
            })
          ).resolves.toBeTruthy()

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              bookingContact: 'invalid-email',
            })
          ).rejects.toThrow(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              bookingContact: 'user@passculture.app',
            })
          ).rejects.toThrow('Ce mail doit vous appartenir')
        })

        it('should validate bookingEmail correctly when receiveNotificationEmails is true', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: [],
          })
          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              receiveNotificationEmails: true,
              bookingEmail: 'valid@example.com',
            })
          ).resolves.toBeTruthy()

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              receiveNotificationEmails: true,
              bookingEmail: 'invalid-email',
            })
          ).rejects.toThrow(
            'Veuillez renseigner un email valide, exemple : mail@exemple.com'
          )
        })

        it('should validate externalTicketOfficeUrl correctly', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: [],
          })
          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              externalTicketOfficeUrl: 'https://example.com',
            })
          ).resolves.toBeTruthy()

          await expect(
            schema.validate({
              ...validInformationFormValuesBase,
              externalTicketOfficeUrl: 'invalid-url',
            })
          ).rejects.toThrow(
            'Veuillez renseigner une URL valide. Ex : https://exemple.com'
          )
        })

        it('should validate address correctly', async () => {
          const schema = getValidationSchema({
            ...baseParams,
            conditionalFields: [],
          })

          await expect(
            schema.validate(validInformationFormValuesBase)
          ).resolves.toBeTruthy()

          const valuesWithoutSelectedOfferLocation = {
            ...validInformationFormValuesBase,
            offerLocation: '',
          }
          await expect(
            schema.validate(valuesWithoutSelectedOfferLocation)
          ).rejects.toThrow('Veuillez sélectionner un choix')

          const virtualSchema = getValidationSchema({
            ...baseParams,
            conditionalFields: [],
            isOfferOnline: true,
          })
          await expect(
            virtualSchema.validate({
              ...validInformationFormValuesBase,
              url: 'https://example.com',
            })
          ).resolves.toBeTruthy()
        })
      })
    }
  )

  describe('with isNewOfferCreationFlowFeatureActive = false', () => {
    const baseParams = {
      conditionalFields: [],
      isNewOfferCreationFlowFeatureActive: false,
      isOfferOnline: false,
    }

    const validInformationFormValuesBase: UsefulInformationFormValues = {
      locationLabel: 'label',
      offerLocation: 'location',
      addressAutocomplete: 'autocomplete',
      street: 'street',
      postalCode: '93160',
      city: 'city',
    }

    it('should validate accessibility correctly', async () => {
      const schema = getValidationSchema(baseParams)

      await expect(
        schema.validate({
          ...validInformationFormValuesBase,
          accessibility: {
            mental: true,
            audio: false,
            visual: false,
            motor: false,
            none: false,
          },
        })
      ).resolves.toBeTruthy()

      await expect(
        schema.validate({
          ...validInformationFormValuesBase,
          accessibility: {
            mental: false,
            audio: false,
            visual: false,
            motor: false,
            none: false,
          },
        })
      ).rejects.toThrow(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    })
  })

  describe('with isNewOfferCreationFlowFeatureActive = true', () => {
    const baseParams = {
      conditionalFields: [],
      isNewOfferCreationFlowFeatureActive: true,
    }

    const validInformationFormValuesBase: UsefulInformationFormValues = {}

    it('should require a valid URL when it is an online offer', async () => {
      const schema = getValidationSchema({
        ...baseParams,
        isOfferOnline: true,
      })

      await expect(
        schema.validate(validInformationFormValuesBase)
      ).rejects.toThrow('Veuillez renseigner une URL valide')

      const dataWithInvalidUrl = {
        ...validInformationFormValuesBase,
        url: 'not-a-url',
      }
      await expect(schema.validate(dataWithInvalidUrl)).rejects.toThrow(
        'Veuillez renseigner une URL valide'
      )

      const dataWithValidUrl = {
        ...validInformationFormValuesBase,
        url: 'https://example.com',
      }
      await expect(schema.validate(dataWithValidUrl)).resolves.toBeDefined()
    })

    it('should NOT require an URL when it is NOT an online offer', async () => {
      const schema = getValidationSchema({
        ...baseParams,
        isOfferOnline: false,
      })

      await expect(
        schema.validate({
          ...validInformationFormValuesBase,
          locationLabel: 'label',
          offerLocation: 'location',
          addressAutocomplete: 'autocomplete',
          street: 'street',
          postalCode: '93160',
          city: 'city',
        })
      ).resolves.toBeDefined()
    })
  })
})
