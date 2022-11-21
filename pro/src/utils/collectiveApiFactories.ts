import {
  GetCollectiveOfferCollectiveStockResponseModel,
  GetCollectiveOfferManagingOffererResponseModel,
  GetCollectiveOfferVenueResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { CollectiveOffer, CollectiveOfferTemplate } from 'core/OfferEducational'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1

const sharedCollectiveOfferData = {
  isActive: true,
  status: OfferStatus.ACTIVE,
  isCancellable: true,
  isTemplate: true,
  name: 'Offre de test',
  bookingEmails: ['toto@example.com'],
  contactEmail: 'toto@example.com',
  contactPhone: '0600000000',
  dateCreated: new Date().toISOString(),
  description: 'blablabla,',
  domains: [{ id: 1, name: 'Danse' }],
  hasBookingLimitDatetimesPassed: false,
  interventionArea: ['mainland'],
  isEditable: true,
  nonHumanizedId: 123,
  offerVenue: {
    venueId: '',
    otherAddress: 'A la mairie',
    addressType: OfferAddressType.OTHER,
  },
  students: [StudentLevels.COLL_GE_3E],
  subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
  venueId: 'VENUE_ID',
  imageUrl: 'https://example.com/image.jpg',
  imageCredit: 'image credit',
}

export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<CollectiveOffer> = {},
  customStock: GetCollectiveOfferCollectiveStockResponseModel = collectiveStockFactory() ||
    null,
  customVenue: GetCollectiveOfferVenueResponseModel = collectiveOfferVenueFactory()
): CollectiveOffer => {
  const stock = customStock === null ? null : customStock

  return {
    ...sharedCollectiveOfferData,
    id: (offerId++).toString(),
    venue: customVenue,
    isBookable: true,
    isVisibilityEditable: true,
    isTemplate: false,
    collectiveStock: stock,
    ...customCollectiveOffer,
  }
}

export const collectiveStockFactory = (
  customStock: Partial<GetCollectiveOfferCollectiveStockResponseModel> = {}
): GetCollectiveOfferCollectiveStockResponseModel => {
  return {
    id: `STOCK${stockId++}`,
    price: 100,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    isBooked: false,
    isCancellable: false,
    isEducationalStockEditable: true,
    ...customStock,
  }
}

export const collectiveOfferTemplateFactory = (
  customCollectiveOfferTemplate: Partial<CollectiveOfferTemplate> = {},
  customVenue: GetCollectiveOfferVenueResponseModel = collectiveOfferVenueFactory()
): CollectiveOfferTemplate => ({
  ...sharedCollectiveOfferData,
  id: (offerId++).toString(),
  venue: customVenue,
  isTemplate: true,
  ...customCollectiveOfferTemplate,
})

export const collectiveOfferVenueFactory = (
  customVenue: Partial<GetCollectiveOfferVenueResponseModel> = {},
  customOfferer: GetCollectiveOfferManagingOffererResponseModel = collectiveOfferOffererFactory()
): GetCollectiveOfferVenueResponseModel => {
  const currentVenueId = venueId++
  return {
    address: 'Ma Rue',
    city: 'Ma Ville',
    id: `VENUE${currentVenueId}`,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: customOfferer,
    managingOffererId: customOfferer.id,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    departementCode: '973',
    fieldsUpdated: [],
    thumbCount: 0,
    ...customVenue,
  }
}

export const collectiveOfferOffererFactory = (
  customOfferer: Partial<GetCollectiveOfferManagingOffererResponseModel> = {}
): GetCollectiveOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    id: `OFFERER${currentOffererId}`,
    name: `La nom de la structure ${currentOffererId}`,
    city: 'Paris',
    dateCreated: new Date().toISOString(),
    isActive: true,
    isValidated: true,
    postalCode: '75018',
    thumbCount: 0,
    ...customOfferer,
  }
}
