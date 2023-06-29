/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { v4 as uuidv4 } from 'uuid'

import {
  PriceCategoryResponseModel,
  SubcategoryIdEnum,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers'
import {
  OfferCategory,
  OfferIndividual,
  OfferIndividualOfferer,
  OfferIndividualStock,
  OfferIndividualVenue,
  OfferSubCategory,
} from 'core/Offers/types'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let priceCategoryId = 1
let offerCategoryId = 1
let offerSubCategoryId = 1

export const individualOfferFactory = (
  customOffer: Partial<OfferIndividual> = {},
  customStock: OfferIndividualStock = individualStockFactory() || null,
  customVenue: OfferIndividualVenue = individualOfferVenueFactory(),
  customPriceCatgory: PriceCategoryResponseModel = priceCategoryFactory() ||
    null
): OfferIndividual => {
  const priceCategory = customPriceCatgory ?? null
  const stock = customStock === null ? null : customStock

  return {
    id: offerId++,
    venue: customVenue,
    name: "Un sale quart d'heure en 3 minutes",
    description: 'Ça va faire mal',
    author: 'Chuck Norris',
    bookingEmail: 'chuck@nofucks.given',
    musicType: 'douleur',
    musicSubType: 'cassage de genoux',
    durationMinutes: 3,
    offererId: customVenue.offerer.id,
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
    isDuo: true,
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
    venueId: 1,
    stocks: stock ? [stock] : [],
    priceCategories: priceCategory ? [priceCategory] : [],
    ...customOffer,
  }
}

export const individualStockFactory = (
  customStock: Partial<OfferIndividualStock> = {}
): OfferIndividualStock => {
  const id = stockId++
  return {
    id: id,
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
    quantity: 18,
    activationCodesExpirationDatetime: null,
    activationCodes: [],
    ...customStock,
  }
}

export const individualOfferVenueFactory = (
  customVenue: Partial<OfferIndividualVenue> = {},
  customOfferer: OfferIndividualOfferer = individualOfferOffererFactory()
): OfferIndividualVenue => {
  const currentVenueId = venueId++

  return {
    id: currentVenueId,
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
  customOfferer: Partial<OfferIndividualOfferer> = {}
): OfferIndividualOfferer => {
  const currentOffererId = offererId++

  return {
    id: currentOffererId,
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

export const individualOfferCategoryFactory = (
  customOfferCategory: Partial<OfferCategory> = {}
): OfferCategory => ({
  id: String(offerCategoryId++),
  proLabel: `catégorie ${offerCategoryId}`,
  isSelectable: true,
  ...customOfferCategory,
})

export const individualOfferSubCategoryFactory = (
  customOfferSubCategory: Partial<OfferSubCategory> = {}
): OfferSubCategory => ({
  id: String(offerSubCategoryId++),
  categoryId: 'A',
  proLabel: `sous catégorie ${offerSubCategoryId}`,
  isEvent: false,
  conditionalFields: [],
  canBeDuo: false,
  canBeEducational: false,
  canBeWithdrawable: false,
  onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
  isSelectable: true,
  ...customOfferSubCategory,
})

export const individualStockEventListFactory = (
  customStock: Partial<StocksEvent> = {}
): StocksEvent => {
  return {
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    priceCategoryId: 2,
    quantity: 18,
    uuid: uuidv4(),
    ...customStock,
  }
}
