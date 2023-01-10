/* istanbul ignore file: DEBT, TO FIX */
import '@testing-library/jest-dom'

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
      venueId: 'AB',
      withdrawalDelay: 12,
      withdrawalDetails: 'withdrawal description',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      durationMinutes: 140,
      bookingEmail: 'test@email.com',
      externalTicketOfficeUrl: 'https://example.com',
    }

    const offerId = 'AAAA'
    const offer = {
      id: offerId,
    } as IOfferIndividual

    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    updateIndividualOffer({ offer, formValues })
    expect(api.patchOffer).toHaveBeenCalledWith(offerId, expectedBody)
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
      bookingEmail: null,
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
      venueId: undefined,
      visualDisabilityCompliant: true,
      withdrawalDelay: null,
      withdrawalDetails: null,
      withdrawalType: undefined,
    }

    const offerId = 'AAAA'
    const offer = {
      id: offerId,
      lastProvider: {
        name: 'provider',
      },
    } as IOfferIndividual
    jest
      .spyOn(api, 'patchOffer')
      .mockResolvedValue({} as GetIndividualOfferResponseModel)

    updateIndividualOffer({ offer, formValues })
    expect(api.patchOffer).toHaveBeenCalledWith(offerId, expectedBody)
  })
})
