/* istanbul ignore file: DEBT, TO FIX */
import { PatchOfferBodyModel } from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { individualOfferFactory } from 'utils/individualApiFactories'

import {
  serializeDurationMinutes,
  serializeExtraData,
  serializePatchOffer,
} from '../serializers'

describe('test updateIndividualOffer::serializers', () => {
  it('test serializeDurationMinutes', () => {
    expect(serializeDurationMinutes('2:15')).toEqual(135)
  })
  it('test serializeDurationMinutes with empty input', () => {
    expect(serializeDurationMinutes('  ')).toBeUndefined()
  })
  it('test serializeExtraData', () => {
    const formValues: IOfferIndividualFormValues = {
      author: 'author value',
      ean: 'ean value',
      musicType: 'musicType value',
      musicSubType: 'musicSubType value',
      performer: 'performer value',
      showType: 'showType value',
      showSubType: 'showSubType value',
      speaker: 'speaker value',
      stageDirector: 'stageDirector value',
      visa: 'visa value',
      // some not extra data fields
      name: 'Test name',
      description: 'Test description',
    } as IOfferIndividualFormValues

    const extraData: IOfferExtraData = {
      author: 'author value',
      ean: 'ean value',
      musicType: 'musicType value',
      musicSubType: 'musicSubType value',
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
    let formValues: IOfferIndividualFormValues
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
        musicType: 'test musicType',
        musicSubType: 'test musicSubType',
        withdrawalDetails: 'test withdrawalDetails',
        withdrawalDelay: undefined,
        withdrawalType: undefined,
        accessibility: {
          [AccessiblityEnum.AUDIO]: true,
          [AccessiblityEnum.MENTAL]: true,
          [AccessiblityEnum.MOTOR]: true,
          [AccessiblityEnum.VISUAL]: true,
          [AccessiblityEnum.NONE]: false,
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
      } as IOfferIndividualFormValues
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
        serializePatchOffer({ offer: individualOfferFactory(), formValues })
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
        serializePatchOffer({ offer: individualOfferFactory(), formValues })
      ).toEqual(patchBody)
    })
  })
})
