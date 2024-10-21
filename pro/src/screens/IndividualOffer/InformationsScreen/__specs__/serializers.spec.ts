/* istanbul ignore file: DEBT, TO FIX */
import { PatchOfferBodyModel, PostOfferBodyModel } from 'apiClient/v1'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { getIndividualOfferFactory } from 'commons/utils/individualApiFactories'
import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'

import {
  serializeDurationMinutes,
  serializeExtraData,
  serializePatchOffer,
} from '../serializePatchOffer'

describe('test updateIndividualOffer::serializers', () => {
  it('test serializeDurationMinutes', () => {
    expect(serializeDurationMinutes('2:15')).toEqual(135)
  })
  it('test serializeDurationMinutes with empty input', () => {
    expect(serializeDurationMinutes('  ')).toBeUndefined()
  })
  it('test serializeExtraData', () => {
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
    expect(serializeExtraData(formValues)).toEqual(extraData)
  })

  describe('test serializePatchOffer', () => {
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
        isVenueVirtual: false,
        city: 'Paris',
        latitude: '48.853320',
        longitude: '2.348979',
        postalCode: '75001',
        street: '3 Rue de Valois',
        locationLabel: 'Ville lumière',
        manuallySetAddress: false,
        offerlocation: OFFER_LOCATION.OTHER_ADDRESS,
      }
      patchBody = {
        audioDisabilityCompliant: true,
        description: 'test description',
        extraData: serializeExtraData(formValues),
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
      }
      patchBody = {
        ...patchBody,
        bookingEmail: null,
        durationMinutes: undefined,
        url: undefined,
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

    it('should send isVenueAddress flag set to true when user select the venue location', () => {
      formValues = {
        ...formValues,
        offerlocation: '1', // any ID that represents the venue OA location
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

    it('should send isVenueAddress flag set to false when user select another location (WIP_ENABLE_OFFER_ADDRESS)', () => {
      formValues = {
        ...formValues,
        offerlocation: OFFER_LOCATION.OTHER_ADDRESS, // user choosed to set another address
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
        offerlocation: OFFER_LOCATION.OTHER_ADDRESS,
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
