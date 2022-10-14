import { serializeApiErrors } from 'apiClient/helpers'
import { PatchOfferBodyModel } from 'apiClient/v1'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import {
  serializeDurationMinutes,
  serializeExtraData,
  serializePatchOffer,
} from '../serializers'

describe('test updateIndividualOffer::serializers', () => {
  it('test serializeApiErrors', () => {
    const apiErrors = {
      name: 'wrong name',
      optIn: 'you must optin our mailing list!',
      venue: 'wrong venue',
    }
    const apiFieldsMap: Record<string, string> = {
      venue: 'venueId',
    }
    expect(serializeApiErrors(apiFieldsMap, apiErrors)).toEqual({
      name: 'wrong name',
      optIn: 'you must optin our mailing list!',
      venueId: 'wrong venue',
    })
  })
  it('test serializeDurationMinutes', () => {
    expect(serializeDurationMinutes('2:15')).toEqual(135)
  })
  it('test serializeDurationMinutes with empty input', () => {
    expect(serializeDurationMinutes('  ')).toBeNull()
  })
  it('test serializeExtraData', () => {
    const formValues: IOfferIndividualFormValues = {
      author: 'author value',
      isbn: 'isbn value',
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
      isbn: 'isbn value',
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
        withdrawalDelay: null,
        withdrawalType: null,
        accessibility: {
          [AccessiblityEnum.AUDIO]: true,
          [AccessiblityEnum.MENTAL]: true,
          [AccessiblityEnum.MOTOR]: true,
          [AccessiblityEnum.VISUAL]: true,
          [AccessiblityEnum.NONE]: false,
        },
        author: 'test author',
        isbn: 'test isbn',
        performer: 'test performer',
        speaker: 'test speaker',
        stageDirector: 'test stageDirector',
        visa: 'test visa',
        durationMinutes: '2:00',
        receiveNotificationEmails: true,
        bookingEmail: 'booking@email.org',
        isDuo: false,
        externalTicketOfficeUrl: 'http://external.url',
        url: 'http://my.url',
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
        url: 'http://my.url',
        venueId: 'test venueId',
        visualDisabilityCompliant: true,
        withdrawalDelay: null,
        withdrawalDetails: 'test withdrawalDetails',
        withdrawalType: null,
        durationMinutes: 120,
        bookingEmail: 'booking@email.org',
        externalTicketOfficeUrl: 'http://external.url',
      }
    })

    it('should serialize patchBody', () => {
      expect(serializePatchOffer(formValues)).toEqual(patchBody)
    })
    it('should serialize patchBody with default', () => {
      formValues = {
        ...formValues,
        receiveNotificationEmails: false,
        durationMinutes: undefined,
      }
      patchBody = {
        ...patchBody,
        bookingEmail: null,
        durationMinutes: null,
      }
      expect(serializePatchOffer(formValues)).toEqual(patchBody)
    })
  })
})
