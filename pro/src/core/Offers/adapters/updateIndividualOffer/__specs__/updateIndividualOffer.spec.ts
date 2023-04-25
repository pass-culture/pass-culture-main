/* istanbul ignore file: DEBT, TO FIX */

import { api } from 'apiClient/api'
import {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { IOfferIndividual } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

import { updateIndividualOffer } from '..'
import { serializePatchOffer } from '../serializers'

describe('updateIndividualOffer', () => {
  it('should sent PatchOfferBodyModel to api', async () => {
    const formValues: IOfferIndividualFormValues = {
      name: 'Test offer',
      description: 'Description for testing offer',
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isNational: true,
      isDuo: true,
      venueId: 'AB',
      withdrawalDelay: 12,
      withdrawalDetails: 'withdrawal description',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      isEvent: true,
      subCategoryFields: [],
      offererId: 'BB',
      categoryId: 'CA',
      subcategoryId: 'SCA',
      showType: '',
      showSubType: '',
      musicType: '',
      musicSubType: '',
      author: 'John Author',
      isbn: undefined,
      performer: 'John Performer',
      speaker: 'John Speaker',
      stageDirector: 'John Stage Director',
      visa: undefined,
      durationMinutes: '2:20',
      receiveNotificationEmails: true,
      bookingEmail: 'test@email.com',
      externalTicketOfficeUrl: 'https://example.com',
      url: '',
    }

    const expectedBody: PatchOfferBodyModel = {
      audioDisabilityCompliant: true,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      visualDisabilityCompliant: true,
      description: 'Description for testing offer',
      extraData: {
        author: 'John Author',
        isbn: undefined,
        musicType: '',
        musicSubType: '',
        performer: 'John Performer',
        showType: '',
        showSubType: '',
        speaker: 'John Speaker',
        stageDirector: 'John Stage Director',
        visa: undefined,
      },
      isNational: true,
      isDuo: true,
      name: 'Test offer',
      url: undefined,
      withdrawalDelay: 12,
      withdrawalDetails: 'withdrawal description',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      durationMinutes: 140,
      bookingEmail: 'test@email.com',
      externalTicketOfficeUrl: 'https://example.com',
      shouldSendMail: false,
    }

    const nonHumanizedofferId = 1234
    const offer = {
      id: 'AAAA',
      nonHumanizedId: nonHumanizedofferId,
    } as IOfferIndividual

    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    await updateIndividualOffer({
      serializedOffer: serializePatchOffer({ offer, formValues }),
      offerId: offer.nonHumanizedId,
    })
    expect(api.patchOffer).toHaveBeenCalledWith(
      nonHumanizedofferId,
      expectedBody
    )
  })

  it('should sent PatchOfferBodyModel to api with provider editable params', async () => {
    const formValues: IOfferIndividualFormValues = {
      name: 'Test offer',
      description: 'Description for testing offer',
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isNational: true,
      isDuo: true,
      venueId: 'AB',
      withdrawalDelay: 12,
      withdrawalDetails: 'withdrawal description',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      isEvent: true,
      subCategoryFields: [],
      offererId: 'BB',
      categoryId: 'CA',
      subcategoryId: 'SCA',
      showType: '',
      showSubType: '',
      musicType: '',
      musicSubType: '',
      author: 'John Author',
      isbn: undefined,
      performer: 'John Performer',
      speaker: 'John Speaker',
      stageDirector: 'John Stage Director',
      visa: undefined,
      durationMinutes: '2:20',
      receiveNotificationEmails: true,
      bookingEmail: 'test@email.com',
      externalTicketOfficeUrl: 'https://example.com',
      url: '',
    }

    const expectedBody: PatchOfferBodyModel = {
      audioDisabilityCompliant: true,
      bookingEmail: undefined,
      description: undefined,
      durationMinutes: undefined,
      externalTicketOfficeUrl: 'https://example.com',
      extraData: undefined,
      isDuo: false,
      isNational: undefined,
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: true,
      name: undefined,
      url: undefined,
      visualDisabilityCompliant: true,
      withdrawalDelay: null,
      withdrawalDetails: undefined,
      withdrawalType: undefined,
      shouldSendMail: false,
    }

    const nonHumanizedofferId = 1234
    const offer = {
      id: 'AAAA',
      nonHumanizedId: nonHumanizedofferId,
      lastProvider: {
        name: 'provider',
      },
    } as IOfferIndividual
    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    await updateIndividualOffer({
      serializedOffer: serializePatchOffer({ offer, formValues }),
      offerId: offer.nonHumanizedId,
    })
    expect(api.patchOffer).toHaveBeenCalledWith(
      nonHumanizedofferId,
      expectedBody
    )
  })
})
