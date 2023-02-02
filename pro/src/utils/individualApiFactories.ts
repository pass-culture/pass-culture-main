import {
  PriceCategoryResponseModel,
  SubcategoryIdEnum,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import {
  IOfferIndividual,
  IOfferIndividualOfferer,
  IOfferIndividualStock,
  IOfferIndividualVenue,
} from 'core/Offers/types'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let priceCategoryId = 1

export const individualOfferFactory = (
  customOffer: Partial<IOfferIndividual> = {},
  customStock: IOfferIndividualStock = individualStockFactory() || null,
  customVenue: IOfferIndividualVenue = individualOfferVenueFactory(),
  customPriceCatgory: PriceCategoryResponseModel = priceCategoryFactory() ||
    null
): IOfferIndividual => {
  const priceCategory = customPriceCatgory ?? null
  const stock = customStock === null ? null : customStock
  const id = (offerId++).toString()

  return {
    id,
    nonHumanizedId: offerId,
    venue: customVenue,
    name: "Un sale quart d'heure en 3 minutes",
    description: 'Ça va faire mal',
    author: 'Chuck Norris',
    bookingEmail: 'chuck@nofucks.given',
    musicType: 'douleur',
    musicSubType: 'cassage de genoux',
    durationMinutes: 3,
    offererId: 'chuck.norris',
    offererName: 'Chuck Norris',
    performer: 'Le Poing de Chuck',
    ean: "Chuck n'est pas identifiable par un EAN",
    showType: 'Cinéma',
    showSubType: 'PEGI 18',
    stageDirector: 'JCVD',
    speaker: "Chuck Norris n'a pas besoin de doubleur",
    url: 'http://chucknorrisfacts.fr/',
    visa: 'USA',
    withdrawalDetails: 'Vient le chercher',
    withdrawalType: WithdrawalTypeEnum.ON_SITE,
    lastProviderName: null,
    lastProvider: null,
    externalTicketOfficeUrl: '',
    isbn: 'isbn',
    isDuo: true,
    isEducational: true,
    isEvent: true,
    isDigital: false,
    accessibility: {
      visual: true,
      mental: true,
      motor: true,
      audio: true,
      none: false,
    },
    isNational: true,
    isActive: true,
    status: OfferStatus.ACTIVE,
    subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
    venueId: 'VENUE_ID',
    stocks: stock ? [stock] : [],
    priceCategories: priceCategory ? [priceCategory] : [],
    ...customOffer,
  }
}

export const individualStockFactory = (
  customStock: Partial<IOfferIndividualStock> = {}
): IOfferIndividualStock => {
  return {
    id: `STOCK${stockId++}`,
    offerId: 'OFFER_ID',
    price: 100,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    bookingsQuantity: 10,
    remainingQuantity: 8,
    dateCreated: new Date('2021-09-01T12:00:00Z'),
    isEventDeletable: true,
    isEventExpired: false,
    isSoftDeleted: false,
    hasActivationCode: false,
    activationCodesExpirationDatetime: null,
    activationCodes: [],
    ...customStock,
  }
}

export const individualOfferVenueFactory = (
  customVenue: Partial<IOfferIndividualVenue> = {},
  customOfferer: IOfferIndividualOfferer = individualOfferOffererFactory()
): IOfferIndividualVenue => {
  const currentVenueId = venueId++

  return {
    id: `VENUE${currentVenueId}`,
    address: 'Ma Rue',
    city: 'Ma Ville',
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    departmentCode: '78',
    accessibility: {
      visual: true,
      mental: true,
      motor: true,
      audio: true,
      none: false,
    },
    offerer: customOfferer,
    ...customVenue,
  }
}

export const individualOfferOffererFactory = (
  customOfferer: Partial<IOfferIndividualOfferer> = {}
): IOfferIndividualOfferer => {
  const currentOffererId = offererId++

  return {
    id: `OFFERER${currentOffererId}`,
    nonHumanizedId: currentOffererId,
    name: `La nom de la structure ${currentOffererId}`,
    ...customOfferer,
  }
}

export const priceCategoryFactory = (
  customPriceCategories: Partial<PriceCategoryResponseModel> = {}
): PriceCategoryResponseModel => ({
  id: priceCategoryId++,
  label: 'mon label',
  price: 66.6,
  ...customPriceCategories,
})
