import {
  ArtistType,
  type CategoryResponseModel,
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
  type SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from '@/apiClient/v1'
import { CATEGORY_STATUS } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'

import { serializeArtist, serializeOfferSectionData } from '../serializer'

describe('IndividualOfferSummary:serializer', () => {
  let offer: GetIndividualOfferWithAddressResponseModel
  let categories: CategoryResponseModel[]
  let subCategoryList: SubcategoryResponseModel[]

  beforeEach(() => {
    offer = getIndividualOfferFactory({
      id: 12,
      extraData: {
        author: 'Offer author',
        performer: 'Offer performer',
        ean: '',
        showSubType: '',
        showType: '',
        stageDirector: 'Offer stageDirector',
        speaker: 'Offer speaker',
        visa: '',
      },
      bookingEmail: 'booking@email.com',
      bookingContact: 'alfonsoLeBg@exampple.com',
      description: 'Offer description',
      durationMinutes: 140,
      isDuo: false,
      name: 'Offer name',
      subcategoryId: SubcategoryIdEnum.CONCERT,
      url: 'https://offer.example.com',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      status: OfferStatus.ACTIVE,
    })
    categories = [
      {
        id: 'CID',
        proLabel: 'Catégorie',
        isSelectable: true,
      },
    ]
    subCategoryList = [
      subcategoryFactory({
        id: SubcategoryIdEnum.CONCERT,
        categoryId: 'CID',
        proLabel: 'sub-category proLabel',
        isEvent: true,
        conditionalFields: ['stageDirector', 'speaker', 'author', 'performer'],
        canBeDuo: true,
        onlineOfflinePlatform: CATEGORY_STATUS.OFFLINE,
        canBeWithdrawable: false,
      }),
    ]
  })

  it('should serialize data with event stock', () => {
    const areArtistsEnabled = false

    const offerSerialized = serializeOfferSectionData(
      offer,
      categories,
      subCategoryList,
      areArtistsEnabled
    )

    expect(offerSerialized).toEqual({
      artistOfferLinks: [],
      id: 12,
      name: 'Offer name',
      description: 'Offer description',
      categoryName: 'Catégorie',
      subCategoryName: 'sub-category proLabel',
      subcategoryId: SubcategoryIdEnum.CONCERT,
      venueName: 'Nom de la structure 1',
      venuePublicName: 'Nom public de la structure 1',
      venueDepartmentCode: '78',
      offererName: "Le nom de l'entité 1",
      bookingEmail: 'booking@email.com',
      bookingContact: 'alfonsoLeBg@exampple.com',
      withdrawalDetails: 'Offer withdrawalDetails',
      withdrawalDelay: 140,
      withdrawalType: WithdrawalTypeEnum.ON_SITE,
      isDuo: false,
      url: 'https://offer.example.com',
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
      gtl_id: undefined,
      isProductBased: false,
      durationMinutes: '140',
      status: OfferStatus.ACTIVE,
    })
  })

  it('should serialize data with showType', () => {
    const areArtistsEnabled = false
    offer = {
      ...offer,
      extraData: {
        ...offer.extraData,
        showType: '400',
        showSubType: '401',
      },
    }
    const offerSerialized = serializeOfferSectionData(
      offer,
      categories,
      subCategoryList,
      areArtistsEnabled
    )
    expect(offerSerialized.showTypeName).toEqual('Humour / Café-théâtre')
    expect(offerSerialized.showSubTypeName).toEqual('Café Théâtre')
  })

  it('should serialize artists', () => {
    const areArtistsEnabled = true

    offer = {
      ...offer,
      artistOfferLinks: [
        {
          artistId: '1',
          artistType: ArtistType.AUTHOR,
          artistName: 'Jean-Michel Jarre',
        },
        {
          artistId: '3',
          artistType: ArtistType.PERFORMER,
          artistName: 'Bobby Vinton',
        },
        {
          artistId: '5',
          artistType: ArtistType.STAGE_DIRECTOR,
          artistName: 'Robert Redford',
        },
        {
          artistId: '6',
          artistType: ArtistType.STAGE_DIRECTOR,
          artistName: 'Jim Carrey',
        },
      ],
    }

    const offerSerialized = serializeOfferSectionData(
      offer,
      categories,
      subCategoryList,
      areArtistsEnabled
    )
    expect(offerSerialized.author).toEqual('Jean-Michel Jarre')
    expect(offerSerialized.performer).toEqual('Bobby Vinton')
    expect(offerSerialized.stageDirector).toEqual('Robert Redford, Jim Carrey')
  })
})

describe('serializeArtist', () => {
  it('should get data from extraData when artist are not enabled', () => {
    const offer = getIndividualOfferFactory({
      extraData: {
        author: 'Offer author',
        performer: 'Offer performer',
        stageDirector: 'Offer stageDirector',
      },
      artistOfferLinks: [
        {
          artistId: '1',
          artistType: ArtistType.AUTHOR,
          artistName: 'Jean-Michel Jarre',
        },
      ],
      productId: undefined,
    })
    const areArtistsEnabled = false
    const defaultValue = 'default'

    const result = serializeArtist(
      offer,
      { areArtistsEnabled },
      offer.extraData.author,
      defaultValue,
      ArtistType.AUTHOR
    )

    expect(result).toBe('Offer author')
  })

  it('should get data from extraData when offer is product based', () => {
    const offer = getIndividualOfferFactory({
      extraData: {
        author: 'Offer author',
        performer: 'Offer performer',
        stageDirector: 'Offer stageDirector',
      },
      artistOfferLinks: [
        {
          artistId: '1',
          artistType: ArtistType.AUTHOR,
          artistName: 'Jean-Michel Jarre',
        },
      ],
      productId: 123,
    })
    const areArtistsEnabled = false
    const defaultValue = 'default'

    const result = serializeArtist(
      offer,
      { areArtistsEnabled },
      offer.extraData.author,
      defaultValue,
      ArtistType.AUTHOR
    )

    expect(result).toBe('Offer author')
  })

  it('should get data from artistOfferLink when offer is not product based and FF WIP_OFFER_ARTISTS is activated and offer is not product based ', () => {
    const offer = getIndividualOfferFactory({
      extraData: {
        author: 'Offer author',
        performer: 'Offer performer',
        stageDirector: 'Offer stageDirector',
      },
      artistOfferLinks: [
        {
          artistId: '1',
          artistType: ArtistType.AUTHOR,
          artistName: 'Jean-Michel Jarre',
        },
      ],
      productId: undefined,
    })
    const areArtistsEnabled = true
    const defaultValue = 'default'

    const result = serializeArtist(
      offer,
      { areArtistsEnabled },
      offer.extraData.author,
      defaultValue,
      ArtistType.AUTHOR
    )

    expect(result).toBe('Jean-Michel Jarre')
  })

  it('should fallback to default value when artist are not find', () => {
    const offer = getIndividualOfferFactory({
      extraData: {
        author: 'Offer author',
        performer: 'Offer performer',
        stageDirector: 'Offer stageDirector',
      },
      artistOfferLinks: [],
      productId: undefined,
    })
    const areArtistsEnabled = true
    const defaultValue = 'default'

    const result = serializeArtist(
      offer,
      { areArtistsEnabled },
      offer.extraData.author,
      defaultValue,
      ArtistType.AUTHOR
    )

    expect(result).toBe('default')
  })
})
