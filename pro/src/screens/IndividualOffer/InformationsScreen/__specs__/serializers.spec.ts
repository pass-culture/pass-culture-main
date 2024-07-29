/* istanbul ignore file: DEBT, TO FIX */
import { PatchOfferBodyModel, PostOfferBodyModel } from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { AccessibilityEnum } from 'core/shared/types'
import { getIndividualOfferFactory } from 'utils/individualApiFactories'

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
      gtlId: '',
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
      gtlId: '',
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
        isDuo: false,
        externalTicketOfficeUrl: 'https://external.url',
        url: 'https://my.url',
        isVenueVirtual: false,
      } as IndividualOfferFormValues
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
        externalTicketOfficeUrl: 'https://external.url',
        shouldSendMail: false,
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
        externalTicketOfficeUrl: '',
        url: '',
      }
      patchBody = {
        ...patchBody,
        bookingEmail: null,
        durationMinutes: undefined,
        externalTicketOfficeUrl: undefined,
        url: undefined,
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
