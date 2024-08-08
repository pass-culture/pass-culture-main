import {
  CategoryResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from 'utils/individualApiFactories'

import { serializeOfferSectionData } from '../serializer'

describe('routes::Summary::serializers', () => {
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
      subcategoryId: SubcategoryIdEnum.CONCERT,
      venueName: 'Le nom du lieu 1',
      venuePublicName: 'Mon Lieu',
      venueDepartmentCode: '78',
      isVenueVirtual: false,
      offererName: 'Le nom de la structure 1',
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
      durationMinutes: '140',
      status: OfferStatus.ACTIVE,
    })
  })

  it('should serialize data with showType', () => {
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
      subCategoryList
    )
    expect(offerSerialized.showTypeName).toEqual('Humour / Café-théâtre')
    expect(offerSerialized.showSubTypeName).toEqual('Café Théâtre')
  })
})
