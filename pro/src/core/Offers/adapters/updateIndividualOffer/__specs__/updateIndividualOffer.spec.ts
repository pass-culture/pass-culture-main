import '@testing-library/jest-dom'

import { api } from 'apiClient/api'
import { PatchOfferBodyModel, WithdrawalTypeEnum } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

import { updateIndividualOffer } from '..'

describe('updateIndividualOffer', () => {
  it('should sent patPatchOfferBodyModel to api', async () => {
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
      name: 'Test offer',
      venueId: 'AB',
      withdrawalDelay: 12,
      withdrawalDetails: 'withdrawal description',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      durationMinutes: 140,
    }

    const offerId = 'AAAA'
    jest.spyOn(api, 'patchOffer').mockResolvedValue({ id: offerId })

    updateIndividualOffer({ offerId, formValues })
    expect(api.patchOffer).toHaveBeenCalledWith(offerId, expectedBody)
  })
})
