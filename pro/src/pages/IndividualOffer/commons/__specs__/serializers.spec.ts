/* istanbul ignore file: DEBT, TO FIX */

import { PatchOfferBodyModel, PostOfferBodyModel } from 'apiClient/v1'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { getIndividualOfferFactory } from 'commons/utils/factories/individualApiFactories'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'

import {
  serializeDurationMinutes,
  serializeExtraDataForPatch,
  serializePatchOffer,
} from '../serializers'

describe('IndividualOffer:commons:serializers', () => {
  describe('serializeDurationMinutes', () => {
    it('should return undefined when durationHour is empty', () => {
      expect(serializeDurationMinutes('')).toStrictEqual(undefined)
    })

    it('should transform string duration into int minutes', () => {
      expect(serializeDurationMinutes('0:00')).toStrictEqual(0)
      expect(serializeDurationMinutes('0:21')).toStrictEqual(21)
      expect(serializeDurationMinutes('3:03')).toStrictEqual(183)
      expect(serializeDurationMinutes('30:38')).toStrictEqual(1838)
    })
  })

  describe('serializeExtraDataForPatch', () => {
    it('should filter out properties that are not in the extraData', () => {
      const formValues: IndividualOfferFormValues = {
        author: 'author value',
        ean: 'ean value',
        gtl_id: '',
        performer: 'performer value',
        showType: 'showType value',
        showSubType: 'showSubType value',
        speaker: 'speaker value',
        stageDirector: 'stageDirector value',
        visa: 'visa value',
        // some not extra data fields
        name: 'Test name',
        description: 'Test description',
      } as IndividualOfferFormValues

      const extraData: PostOfferBodyModel['extraData'] = {
        author: 'author value',
        ean: 'ean value',
        gtl_id: '',
        performer: 'performer value',
        showType: 'showType value',
        showSubType: 'showSubType value',
        speaker: 'speaker value',
        stageDirector: 'stageDirector value',
        visa: 'visa value',
      }

      expect(serializeExtraDataForPatch(formValues)).toEqual(extraData)
    })
  })

  describe('serializePatchOffer', () => {
    let formValues: IndividualOfferFormValues
    let patchBody: PatchOfferBodyModel

    beforeEach(() => {
      formValues = {
        isEvent: false,
        subCategoryFields: [],
        name: 'test name',
        description: 'test description',
        offererId: 'test offererId',
        venueId: 'test venueId',
        isNational: false,
        categoryId: 'test categoryId',
        subcategoryId: 'test subcategoryId',
        showType: 'test showType',
        showSubType: 'test showSubType',
        gtl_id: '01000000',
        withdrawalDetails: 'test withdrawalDetails',
        withdrawalDelay: undefined,
        withdrawalType: undefined,
        accessibility: {
          [AccessibilityEnum.AUDIO]: true,
          [AccessibilityEnum.MENTAL]: true,
          [AccessibilityEnum.MOTOR]: true,
          [AccessibilityEnum.VISUAL]: true,
          [AccessibilityEnum.NONE]: false,
        },
        author: 'test author',
        ean: 'test ean',
        performer: 'test performer',
        speaker: 'test speaker',
        stageDirector: 'test stageDirector',
        visa: 'test visa',
        durationMinutes: '2:00',
        receiveNotificationEmails: true,
        bookingEmail: 'booking@email.org',
        bookingContact: undefined,
        isDuo: false,
        url: 'https://my.url',
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
        audioDisabilityCompliant: true,
        description: 'test description',
        extraData: serializeExtraDataForPatch(formValues),
        isNational: false,
        isDuo: false,
        mentalDisabilityCompliant: true,
        motorDisabilityCompliant: true,
        name: 'test name',
        url: 'https://my.url',
        visualDisabilityCompliant: true,
        withdrawalDelay: undefined,
        withdrawalDetails: 'test withdrawalDetails',
        withdrawalType: undefined,
        bookingContact: undefined,
        externalTicketOfficeUrl: 'https://my-external-ticket-office.url',
        durationMinutes: 120,
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

    it('should serialize patchBody', () => {
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
        })
      ).toEqual(patchBody)
    })

    it('should serialize patchBody with default', () => {
      formValues = {
        ...formValues,
        receiveNotificationEmails: false,
        durationMinutes: undefined,
        url: '',
        externalTicketOfficeUrl: '',
      }
      patchBody = {
        ...patchBody,
        bookingEmail: null,
        durationMinutes: undefined,
        url: undefined,
        externalTicketOfficeUrl: null,
      }
      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
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
      const { address, ...body } = patchBody

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory({ isDigital: true }),
          formValues,
        })
      ).toEqual(body)
    })

    it('should serialize patchBody with empty address when address did not change', () => {
      formValues = {
        ...formValues,
        city: undefined,
      }
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { address, ...body } = patchBody

      expect(
        serializePatchOffer({
          offer: getIndividualOfferFactory(),
          formValues,
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
        })
      ).toEqual(patchBody)
    })

    it('should trim blank spaces in string fields', () => {
      formValues = {
        ...formValues,
        name: '   test name    ',
        description: '  test description   ',
        withdrawalDetails: '  test withdrawalDetails  ',
        locationLabel: ' test label     ',
        street: '  test street   ',
        city: '    test city     ',
        postalCode: ' test postalCode     ',
      }
      patchBody = {
        ...patchBody,
        name: 'test name',
        description: 'test description',
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
        })
      ).toEqual(patchBody)
    })
  })
})
