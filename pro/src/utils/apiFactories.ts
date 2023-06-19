/* istanbul ignore file */
import {
  GetIndividualOfferResponseModel,
  GetOfferManagingOffererResponseModel,
  GetOfferStockResponseModel,
  GetOfferVenueResponseModel,
  OfferStatus,
  SubcategoryIdEnum,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { BookingRecapStatus } from 'apiClient/v1/models/BookingRecapStatus'

let offerId = 1
let venueId = 1
let offererId = 1
let stockId = 1
let bookingId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer = {},
  customStock = collectiveStockFactory() || null,
  customVenue = getOfferVenueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]
  const currentOfferId = offerId++

  return {
    id: `OFFER${currentOfferId}`,
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isEditable: true,
    isEvent: true,
    isFullyBooked: false,
    isThing: false,
    nonHumanizedId: currentOfferId,
    status: OfferStatus.ACTIVE,
    stocks,
    venue: customVenue,
    hasBookingLimitDatetimesPassed: false,
    isEducational: true,
    ...customCollectiveOffer,
  }
}

const collectiveStockFactory = (customStock = {}) => {
  return {
    bookingsQuantity: 0,
    id: `STOCK${stockId++}`,
    offerId: `OFFER${offerId}`,
    price: 100,
    quantity: 1,
    remainingQuantity: 1,
    beginningDatetime: new Date('2021-10-15T12:00:00Z'),
    bookingLimitdatetime: new Date('2021-09-15T12:00:00Z'),
    ...customStock,
  }
}

export const GetIndividualOfferFactory = (
  customOffer = {},
  customStock = stockFactory() || null,
  customVenue = getOfferVenueFactory()
): GetIndividualOfferResponseModel => {
  const stocks = customStock === null ? [] : [customStock]
  const currentOfferId = offerId++

  return {
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isEditable: true,
    isEvent: false,
    isThing: true,
    nonHumanizedId: currentOfferId,
    status: OfferStatus.ACTIVE,
    stocks,
    venue: customVenue,
    hasBookingLimitDatetimesPassed: false,
    dateCreated: '2020-04-12T19:31:12Z',
    isDigital: false,
    isDuo: true,
    isNational: true,
    subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
    ...customOffer,
  }
}

export const getOfferVenueFactory = (
  customVenue = {},
  customOfferer = offererFactory()
): GetOfferVenueResponseModel => {
  const currentVenueId = venueId++
  return {
    address: 'Ma Rue',
    city: 'Ma Ville',
    nonHumanizedId: currentVenueId,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: customOfferer,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    departementCode: '973',
    ...customVenue,
  }
}

export const getVenueListItemFactory = (
  customVenue = {},
  customOfferer = offererFactory()
): VenueListItemResponseModel => {
  const currentVenueId = venueId++
  return {
    id: `VENUE${currentVenueId}`,
    nonHumanizedId: currentVenueId,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOffererId: customOfferer.nonHumanizedId.toString(),
    publicName: 'Mon Lieu',
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: true,
    offererName: 'offerer',
    ...customVenue,
  }
}

export const offererFactory = (
  customOfferer = {}
): GetOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    name: `La nom de la structure ${currentOffererId}`,
    nonHumanizedId: 3,
    ...customOfferer,
  }
}

export const stockFactory = (customStock = {}): GetOfferStockResponseModel => {
  const id = stockId++
  return {
    bookingsQuantity: 0,
    nonHumanizedId: id,
    price: 10,
    quantity: null,
    remainingQuantity: 2,
    dateCreated: '2020-04-12T19:31:12Z',
    dateModified: '2020-04-12T19:31:12Z',
    hasActivationCode: false,
    isBookable: true,
    isEventDeletable: true,
    isEventExpired: false,
    isSoftDeleted: false,
    ...customStock,
  }
}

export const bookingRecapFactory = (
  customBookingRecap = {},
  customOffer = {}
) => {
  const offer = GetIndividualOfferFactory(customOffer)

  return {
    beneficiary: {
      email: 'user@example.com',
      firstname: 'First',
      lastname: 'Last',
      phonenumber: '0606060606',
    },
    bookingAmount: 0,
    bookingDate: '2020-04-12T19:31:12Z',
    bookingIsDuo: false,
    bookingId: '1',
    bookingStatus: BookingRecapStatus.BOOKED,
    bookingStatusHistory: [
      {
        date: '2020-04-12T19:31:12Z',
        status: BookingRecapStatus.BOOKED,
      },
    ],
    bookingToken: `TOKEN${bookingId++}`,
    stock: {
      offerIdentifier: 'AA',
      offerId: offer.nonHumanizedId,
      offerName: offer.name,
      offerIsEducational: false,
      stockIdentifier: offer.stocks[0].nonHumanizedId.toString(),
      offerIsbn: '123456789',
    },
    ...customBookingRecap,
  }
}
