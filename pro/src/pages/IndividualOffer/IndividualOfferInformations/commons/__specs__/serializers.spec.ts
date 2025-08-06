/* istanbul ignore file: DEBT, TO FIX */

import { PatchOfferBodyModel } from '@/apiClient/v1'
import { AccessibilityEnum } from '@/commons/core/shared/types'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { getOfferLastProvider } from '@/commons/utils/factories/providerFactories'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'
import { UsefulInformationFormValues } from '@/pages/IndividualOffer/IndividualOfferInformations/commons/types'

import { serializePatchOffer } from '../serializers'

describe('serializePatchOffer', () => {
  let formValues: UsefulInformationFormValues
  let patchBody: PatchOfferBodyModel

  beforeEach(() => {
    formValues = {
      accessibility: {
        [AccessibilityEnum.AUDIO]: true,
        [AccessibilityEnum.MENTAL]: true,
        [AccessibilityEnum.MOTOR]: true,
        [AccessibilityEnum.VISUAL]: true,
        [AccessibilityEnum.NONE]: false,
      },
      isEvent: false,
      isNational: false,
      withdrawalDetails: 'test withdrawalDetails',
      withdrawalDelay: undefined,
      withdrawalType: undefined,
      receiveNotificationEmails: true,
      bookingEmail: 'booking@email.org',
      bookingContact: undefined,
      externalTicketOfficeUrl: 'https://my-external-ticket-office.url',
      city: 'Paris',
      latitude: '48.853320',
      longitude: '2.348979',
      postalCode: '75001',
      street: '3 Rue de Valois',
      locationLabel: 'Ville lumière',
      manuallySetAddress: false,
      offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
    }
    patchBody = {
      isNational: false,
      withdrawalDelay: undefined,
      withdrawalDetails: 'test withdrawalDetails',
      withdrawalType: undefined,
      bookingContact: undefined,
      externalTicketOfficeUrl: 'https://my-external-ticket-office.url',
      bookingEmail: 'booking@email.org',
      shouldSendMail: false,
      address: {
        city: 'Paris',
        latitude: '48.853320',
        longitude: '2.348979',
        postalCode: '75001',
        street: '3 Rue de Valois',
        label: 'Ville lumière',
        isManualEdition: false,
        isVenueAddress: false,
      },
    }
  })

  describe('without Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = false

    beforeEach(() => {
      patchBody = {
        ...patchBody,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: true,
      }
    })

    it('should serialize patchBody', () => {
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it('should serialize patchBody with default', () => {
      formValues = {
        ...formValues,
        receiveNotificationEmails: false,
        externalTicketOfficeUrl: '',
      }
      patchBody = {
        ...patchBody,
        bookingEmail: null,
        externalTicketOfficeUrl: null,
      }
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it('should serialize patchBody with empty address label and manual edition false', () => {
      formValues = {
        ...formValues,
        locationLabel: '',
        manuallySetAddress: false,
      }
      patchBody = {
        ...patchBody,
        address: {
          ...patchBody.address!,
          label: '',
          isManualEdition: false,
        },
      }

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it('should serialize patchBody with empty address when venue is digital', () => {
      formValues = {
        ...formValues,
        locationLabel: '',
        manuallySetAddress: false,
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { address: _address, ...body } = patchBody

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory({ isDigital: true }),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(body)
    })

    it('should serialize patchBody with empty address when address did not change', () => {
      formValues = {
        ...formValues,
        city: undefined,
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { address: _address, ...body } = patchBody

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(body)
    })

    it('should send isVenueAddress flag set to true when user select the venue location', () => {
      formValues = {
        ...formValues,
        offerLocation: '1', // any ID that represents the venue OA location
      }
      patchBody = {
        ...patchBody,
        address: {
          ...patchBody.address!,
          isVenueAddress: true,
        },
      }
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it('should send isVenueAddress flag set to false when user select another location', () => {
      formValues = {
        ...formValues,
        offerLocation: OFFER_LOCATION.OTHER_ADDRESS, // user choosed to set another address
      }
      patchBody = {
        ...patchBody,
        address: {
          ...patchBody.address!,
          isVenueAddress: false,
        },
      }
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)

      // Test with empty label and manual edition false
      formValues = {
        ...formValues,
        locationLabel: '',
        manuallySetAddress: false,
        offerLocation: OFFER_LOCATION.OTHER_ADDRESS,
      }
      patchBody = {
        ...patchBody,
        address: {
          ...patchBody.address!,
          label: '',
          isManualEdition: false,
          isVenueAddress: false,
        },
      }

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it('should trim blank spaces in string fields', () => {
      formValues = {
        ...formValues,
        withdrawalDetails: '  test withdrawalDetails  ',
        locationLabel: ' test label     ',
        street: '  test street   ',
        city: '    test city     ',
        postalCode: ' test postalCode     ',
      }
      patchBody = {
        ...patchBody,
        withdrawalDetails: 'test withdrawalDetails',
        address: {
          ...patchBody.address!,
          label: 'test label',
          street: 'test street',
          city: 'test city',
          postalCode: 'test postalCode',
        },
      }

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
          isNewOfferCreationFlowFeatureActive,
        })
      ).toEqual(patchBody)
    })

    it("should only return accessibility fields when it's a synchronized offer", () => {
      const offer = getIndividualOfferFactory({
        lastProvider: getOfferLastProvider(),
      })
      formValues = {
        ...formValues,
        accessibility: {
          [AccessibilityEnum.AUDIO]: true,
          [AccessibilityEnum.MENTAL]: false,
          [AccessibilityEnum.MOTOR]: true,
          [AccessibilityEnum.VISUAL]: false,
          [AccessibilityEnum.NONE]: false,
        },
      }
      patchBody = {
        ...patchBody,
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: false,
      }

      const result = serializePatchOffer({
        offer,
        formValues,
        isNewOfferCreationFlowFeatureActive,
      })

      expect(result).toEqual({
        audioDisabilityCompliant: true,
        mentalDisabilityCompliant: false,
        motorDisabilityCompliant: true,
        visualDisabilityCompliant: false,
      })
    })
  })

  describe('with Feature Flag', () => {
    const isNewOfferCreationFlowFeatureActive = true

    it('should exclude accessibility fields', () => {
      formValues = {
        ...formValues,
        accessibility: {
          [AccessibilityEnum.AUDIO]: true,
          [AccessibilityEnum.MENTAL]: false,
          [AccessibilityEnum.MOTOR]: true,
          [AccessibilityEnum.VISUAL]: false,
          [AccessibilityEnum.NONE]: false,
        },
      }

      const result = serializePatchOffer({
        offer: getIndividualOfferFactory(),
        formValues,
        isNewOfferCreationFlowFeatureActive,
      })

      expect(result).not.toHaveProperty('audioDisabilityCompliant')
      expect(result).not.toHaveProperty('mentalDisabilityCompliant')
      expect(result).not.toHaveProperty('motorDisabilityCompliant')
      expect(result).not.toHaveProperty('visualDisabilityCompliant')
    })
  })
})
