import { OfferStatus, WithdrawalTypeEnum } from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  OfferCategory,
  OfferIndividual,
  OfferIndividualStock,
  OfferSubCategory,
} from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

import { serializeOfferSectionData } from '../serializer'

describe('routes::Summary::serializers', () => {
  let offer: OfferIndividual
  let categories: OfferCategory[]
  let subCategoryList: OfferSubCategory[]

  beforeEach(() => {
    offer = {
      id: 12,
      author: 'Offer author',
      bookingEmail: 'booking@email.com',
      bookingContact: 'alfonsoLeBg@exampple.com',
      description: 'Offer description',
      durationMinutes: 140,
      isActive: true,
      isDuo: false,
      isEvent: true,
      isDigital: true,
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
      offererId: 12,
      offererName: '',
      performer: 'Offer performer',
      ean: '',
      showSubType: '',
      showType: '',
      stageDirector: 'Offer stageDirector',
      speaker: 'Offer speaker',
      subcategoryId: 'SCID',
      image: {
        originalUrl: 'https://image.url.test',
        url: 'https://image.url.test',
        credit: 'John Do',
      },
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      venueId: 1,
      venue: {
        id: 1,
        name: 'Venue name',
        publicName: 'Venue publicName',
        isVirtual: false,
        address: '15 rue de la corniche',
        postalCode: '75001',
        city: 'Paris',
        offerer: {
          id: 1,
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
      stocks: [
        {
          quantity: 10,
          price: 12,
          bookingLimitDatetime: '01-01-2021',
          beginningDatetime: null,
          dateCreated: new Date('01-12-2020'),
        } as OfferIndividualStock,
        {
          quantity: 10,
          price: 12,
          bookingLimitDatetime: '01-01-2023',
          beginningDatetime: '01-12-2023',
        } as OfferIndividualStock,
        {
          quantity: 10,
          price: 12,
          bookingLimitDatetime: '01-01-2024',
          beginningDatetime: null,
          dateCreated: new Date('01-12-2019'),
        } as OfferIndividualStock,
        {
          quantity: 10,
          price: 12,
          bookingLimitDatetime: '01-01-2022',
          beginningDatetime: '01-12-2022',
        } as OfferIndividualStock,
      ],
      lastProviderName: 'Last Provider Name',
      lastProvider: null,
      status: OfferStatus.ACTIVE,
    }
    categories = [
      {
        id: 'CID',
        proLabel: 'Catégorie',
        isSelectable: true,
      },
    ]
    subCategoryList = [
      {
        id: 'SCID',
        categoryId: 'CID',
        proLabel: 'sub-category proLabel',
        isEvent: true,
        conditionalFields: ['stageDirector', 'speaker', 'author', 'performer'],
        canBeDuo: true,
        canBeEducational: false,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        reimbursementRule: 'sub-category reimbursementRule',
        canBeWithdrawable: false,
        isSelectable: true,
      },
    ]
  })

  it('should serialize data with event stock', () => {
    const offerSerialized = serializeOfferSectionData(
      offer,
      categories,
      subCategoryList
    )

    expect(offerSerialized).toEqual({
      id: 12,
      name: 'Offer name',
      description: 'Offer description',
      categoryName: 'Catégorie',
      subCategoryName: 'sub-category proLabel',
      subcategoryId: 'SCID',
      venueName: 'Venue name',
      venuePublicName: 'Venue publicName',
      venueDepartmentCode: '75',
      isVenueVirtual: false,
      offererName: 'Offerer name',
      bookingEmail: 'booking@email.com',
      bookingContact: 'alfonsoLeBg@exampple.com',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      accessibility: {
        [AccessiblityEnum.AUDIO]: true,
        [AccessiblityEnum.MENTAL]: true,
        [AccessiblityEnum.MOTOR]: true,
        [AccessiblityEnum.VISUAL]: true,
        [AccessiblityEnum.NONE]: false,
      },
      isDuo: false,
      url: 'https://offer.example.com',
      externalTicketOfficeUrl: 'https://external.example.com',
      author: 'Offer author',
      stageDirector: 'Offer stageDirector',
      musicTypeName: '',
      musicSubTypeName: '',
      showTypeName: '',
      showSubTypeName: '',
      speaker: 'Offer speaker',
      visa: '',
      performer: 'Offer performer',
      ean: '',
      durationMinutes: '140',
      status: OfferStatus.ACTIVE,
    })
  })

  it('should serialize data with showType', () => {
    offer = {
      ...offer,
      showType: '400',
      showSubType: '401',
    }
    const offerSerialized = serializeOfferSectionData(
      offer,
      categories,
      subCategoryList
    )
    expect(offerSerialized.showTypeName).toEqual('Humour / Café-théâtre')
    expect(offerSerialized.showSubTypeName).toEqual('Café Théâtre')
  })
})
