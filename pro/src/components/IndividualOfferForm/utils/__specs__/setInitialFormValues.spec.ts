import { SubcategoryResponseModel, WithdrawalTypeEnum } from 'apiClient/v1'
import { IndividualOffer } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { offerVenueFactory, offererFactory } from 'utils/apiFactories'
import {
  individualOfferFactory,
  individualOfferSubCategoryFactory,
} from 'utils/individualApiFactories'

import setInitialFormValues from '../setInitialFormValues'

describe('setFormReadOnlyFields', () => {
  let offer: IndividualOffer
  let subCategoryList: SubcategoryResponseModel[]
  const venueId = 13
  const offererId = 12

  beforeEach(() => {
    offer = individualOfferFactory(
      {
        id: 12,
        author: 'Offer author',
        bookingEmail: 'booking@email.com',
        bookingContact: 'roberto@example.com',
        description: 'Offer description',
        durationMinutes: 140,
        isActive: true,
        isDuo: false,
        isEvent: true,
        isDigital: false,
        accessibility: {
          [AccessiblityEnum.AUDIO]: true,
          [AccessiblityEnum.MENTAL]: true,
          [AccessiblityEnum.MOTOR]: true,
          [AccessiblityEnum.VISUAL]: true,
          [AccessiblityEnum.NONE]: false,
        },
        isNational: false,
        name: 'Offer name',
        musicSubType: '',
        musicType: '',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        stageDirector: 'Offer stageDirector',
        speaker: 'Offer speaker',
        subcategoryId: 'SCID',
        url: 'https://offer.example.com',
        externalTicketOfficeUrl: 'https://external.example.com',
        visa: '',
        withdrawalDetails: 'Offer withdrawalDetails',
        withdrawalDelay: 140,
        withdrawalType: WithdrawalTypeEnum.ON_SITE,
      },
      offerVenueFactory({
        id: venueId,
        managingOfferer: offererFactory({ id: offererId }),
      })
    )
    subCategoryList = [
      individualOfferSubCategoryFactory({
        id: 'SCID',
        categoryId: 'CID',
        isEvent: true,
        conditionalFields: ['stageDirector', 'speaker', 'author', 'performer'],
        canBeDuo: true,
      }),
    ]
  })

  it('should fill initial form values from offer', () => {
    const expectedResult = {
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      bookingEmail: 'booking@email.com',
      bookingContact: 'roberto@example.com',
      categoryId: 'CID',
      description: 'Offer description',
      isEvent: true,
      isNational: false,
      isDuo: false,
      musicSubType: '',
      musicType: '',
      name: 'Offer name',
      offererId: offererId.toString(),
      receiveNotificationEmails: true,
      showSubType: '',
      showType: '',
      subCategoryFields: [
        'stageDirector',
        'speaker',
        'author',
        'performer',
        'durationMinutes',
        'isDuo',
      ],
      subcategoryId: 'SCID',
      venueId: venueId.toString(),
      withdrawalDelay: 140,
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      author: 'Offer author',
      performer: 'Offer performer',
      ean: '',
      speaker: 'Offer speaker',
      stageDirector: 'Offer stageDirector',
      visa: '',
      durationMinutes: '2:20',
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
    }

    const initialFormValues = setInitialFormValues(offer, subCategoryList, true)
    expect(initialFormValues).toStrictEqual(expectedResult)
  })

  it("should throw error if sub category don't exist", () => {
    expect(() => setInitialFormValues(offer, [], true)).toThrow(
      'La categorie de l’offre est introuvable'
    )
  })
})
