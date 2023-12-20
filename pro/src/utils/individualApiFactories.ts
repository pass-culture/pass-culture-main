/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import {
  CategoryResponseModel,
  GetOfferVenueResponseModel,
  GetOfferStockResponseModel,
  GetVenueResponseModel,
  PriceCategoryResponseModel,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  VenueTypeCode,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OfferStatus } from 'apiClient/v2'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { IndividualOfferContextValues } from 'context/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { IndividualOffer, IndividualOfferStock } from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'

import { offerVenueFactory } from './apiFactories'

let offerId = 1
let stockId = 1
let stockResponseId = 1
let venueId = 1
let priceCategoryId = 1
let offerCategoryId = 1
let offerSubCategoryId = 1

export const individualOfferFactory = (
  customOffer: Partial<IndividualOffer> = {},
  customVenue: GetOfferVenueResponseModel = offerVenueFactory()
): IndividualOffer => {
  return {
    id: offerId++,
    venue: customVenue,
    name: "Un sale quart d'heure en 3 minutes",
    description: 'Ça va faire mal',
    author: 'Chuck Norris',
    bookingEmail: 'chuck@nofucks.given',
    bookingsCount: 18,
    musicType: 'douleur',
    musicSubType: 'cassage de genoux',
    durationMinutes: 3,
    offererId: customVenue.managingOfferer.id,
    offererName: 'Chuck Norris',
    performer: 'Le Poing de Chuck',
    ean: 'Chuck n’est pas identifiable par un EAN',
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
    hasStocks: true,
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
    isActivable: true,
    status: OfferStatus.ACTIVE,
    subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
    venueId: customVenue.id,
    priceCategories: [priceCategoryFactory()],
    ...customOffer,
  }
}

export const individualStockFactory = (
  customStock: Partial<IndividualOfferStock> = {}
): IndividualOfferStock => {
  const id = stockId++
  return {
    id: id,
    price: 100,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    bookingsQuantity: 10,
    remainingQuantity: 8,
    isEventDeletable: true,
    hasActivationCode: false,
    quantity: 18,
    activationCodesExpirationDatetime: null,
    activationCodes: [],
    ...customStock,
  }
}

export const individualOfferVenueItemFactory = (
  customVenue: Partial<IndividualOfferVenueItem> = {}
): IndividualOfferVenueItem => {
  const currentVenueId = venueId++

  return {
    id: currentVenueId,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    accessibility: {
      visual: true,
      mental: true,
      motor: true,
      audio: true,
      none: false,
    },
    managingOffererId: 1,
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: false,
    withdrawalDetails: null,
    venueType: VenueTypeCode.AUTRE,
    ...customVenue,
  }
}

export const individualOfferVenueResponseModelFactory = (
  customVenue: Partial<GetVenueResponseModel> = {}
): GetVenueResponseModel => {
  const currentVenueId = venueId++

  return {
    id: currentVenueId,
    address: 'Ma Rue',
    city: 'Ma Ville',
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    departementCode: '78',
    managingOfferer: {
      city: 'Paris',
      dateCreated: '2021-10-15T12:00:00Z',
      id: 1,
      isValidated: true,
      name: 'managingOffererName',
      postalCode: '78140',
    },
    collectiveDmsApplications: [],
    collectiveDomains: [],
    dateCreated: '2021-10-15T12:00:00Z',
    dmsToken: 'token',
    fieldsUpdated: [],
    hasAdageId: false,
    venueTypeCode: VenueTypeCode.AUTRE,
    ...customVenue,
  }
}

export const individualOfferGetVenuesFactory = (
  customVenue: Partial<VenueListItemResponseModel> = {}
): VenueListItemResponseModel => {
  const currentVenueId = venueId++

  return {
    id: currentVenueId,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    publicName: undefined,
    venueTypeCode: VenueTypeCode.AUTRE,
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: false,
    managingOffererId: 1,
    offererName: 'la structure de Michel',
    ...customVenue,
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
  customOfferCategory: Partial<CategoryResponseModel> = {}
): CategoryResponseModel => ({
  id: String(offerCategoryId++),
  proLabel: `catégorie ${offerCategoryId}`,
  isSelectable: true,
  ...customOfferCategory,
})

export const individualOfferSubCategoryFactory = (
  customOfferSubCategory: Partial<SubcategoryResponseModel> = {}
): SubcategoryResponseModel => ({
  id: String(offerSubCategoryId++),
  categoryId: 'A',
  appLabel: `sous catégorie ${offerSubCategoryId}`,
  proLabel: `sous catégorie ${offerSubCategoryId}`,
  isEvent: false,
  conditionalFields: [],
  canBeDuo: false,
  canBeEducational: false,
  canBeWithdrawable: false,
  onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
  isSelectable: true,
  canExpire: true,
  isDigitalDeposit: false,
  isPhysicalDeposit: true,
  ...customOfferSubCategory,
})

export const individualOfferSubCategoryResponseModelFactory = (
  customOfferSubCategory: Partial<SubcategoryResponseModel> = {}
): SubcategoryResponseModel => ({
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
  appLabel: 'appLabel',
  canExpire: true,
  isDigitalDeposit: true,
  isPhysicalDeposit: true,
  ...customOfferSubCategory,
})

export const individualStockEventFactory = (
  customStock: Partial<StocksEvent> = {}
): StocksEvent => {
  return {
    id: stockId++,
    beginningDatetime: '2021-10-15T12:00:00.000Z',
    bookingLimitDatetime: '2021-09-15T12:00:00.000Z',
    priceCategoryId: 2,
    quantity: 18,
    bookingsQuantity: 0,
    isEventDeletable: true,
    ...customStock,
  }
}

export const individualGetOfferStockResponseModelFactory = (
  customStock: Partial<GetOfferStockResponseModel> = {}
): GetOfferStockResponseModel => {
  return {
    id: stockResponseId++,
    price: 10,
    activationCodesExpirationDatetime: null,
    hasActivationCode: false,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    priceCategoryId: 2,
    quantity: 18,
    bookingsQuantity: 0,
    isEventDeletable: true,
    ...customStock,
  }
}

export const individualOfferContextFactory = (
  customContext: Partial<IndividualOfferContextValues> = {}
): IndividualOfferContextValues => {
  const offer = individualOfferFactory()

  return {
    offerId: offer.id,
    offer,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setOffer: () => {},
    setSubcategory: () => {},
    showVenuePopin: {},
    ...customContext,
  }
}
