import { OfferStatus, WithdrawalTypeEnum } from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferIndividual, IOfferSubCategory } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

import setInitialFormValues from '../setInitialFormValues'

describe('setFormReadOnlyFields', () => {
  let offer: IOfferIndividual
  let subCategoryList: IOfferSubCategory[]
  const venueId = 13
  const offererId = 12

  beforeEach(() => {
    offer = {
      nonHumanizedId: 12,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      description: 'Offer description',
      durationMinutes: 140,
      isbn: '',
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
      offererId: offererId,
      offererName: '',
      performer: 'Offer performer',
      ean: '',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'SCID',
      image: undefined,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      venueId: venueId,
      venue: {
        id: venueId,
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          nonHumanizedId: 1,
          name: 'Offerer name',
        },
        departmentCode: '75',
        accessibility: {
          [AccessiblityEnum.AUDIO]: false,
          [AccessiblityEnum.MENTAL]: false,
          [AccessiblityEnum.MOTOR]: false,
          [AccessiblityEnum.VISUAL]: false,
          [AccessiblityEnum.NONE]: true,
        },
      },
      visa: '',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      stocks: [],
      lastProviderName: null,
      lastProvider: null,
      status: OfferStatus.ACTIVE,
    }
    subCategoryList = [
      {
        id: 'SCID',
        categoryId: 'CID',
        proLabel: 'sub-category proLabel',
        isEvent: true,
        conditionalFields: ['stageDirector', 'speaker', 'author', 'performer'],
        canBeDuo: true,
        canBeEducational: false,
        canBeWithdrawable: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: 'sub-category reimbursementRule',
        isSelectable: true,
      },
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
      isbn: '',
      performer: 'Offer performer',
      ean: '',
      speaker: 'Offer speaker',
      stageDirector: 'Offer stageDirector',
      visa: '',
      durationMinutes: '2:20',
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
    }

    const initialFormValues = setInitialFormValues(offer, subCategoryList)
    expect(initialFormValues).toStrictEqual(expectedResult)
  })

  it("should throw error if sub category don't exist", () => {
    expect(() => setInitialFormValues(offer, [])).toThrow(
      'La categorie de l’offre est introuvable'
    )
  })
})
