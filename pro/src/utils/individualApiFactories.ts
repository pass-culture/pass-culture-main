/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { v4 as uuidv4 } from 'uuid'

import {
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
import {
  OfferCategory,
  IndividualOffer,
  IndividualOfferOfferer,
  IndividualOfferStock,
  IndividualOfferVenue,
  OfferSubCategory,
} from 'core/Offers/types'
import { IndividualOfferVenueItem } from 'core/Venue/types'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let priceCategoryId = 1
let offerCategoryId = 1
let offerSubCategoryId = 1

export const individualOfferFactory = (
  customOffer: Partial<IndividualOffer> = {},
  customStock: IndividualOfferStock = individualStockFactory() || null,
  customVenue: IndividualOfferVenue = individualOfferVenueFactory(),
  customPriceCatgory: PriceCategoryResponseModel = priceCategoryFactory() ||
    null
): IndividualOffer => {
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
  customVenue: Partial<IndividualOfferVenue> = {},
  customOfferer: IndividualOfferOfferer = individualOfferOffererFactory()
): IndividualOfferVenue => {
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
      fieldsUpdated: [],
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

export const individualOfferOffererFactory = (
  customOfferer: Partial<IndividualOfferOfferer> = {}
): IndividualOfferOfferer => {
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

export const individualStockEventListFactory = (
  customStock: Partial<StocksEvent> = {}
): StocksEvent => {
  return {
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    priceCategoryId: 2,
    quantity: 18,
    uuid: uuidv4(),
    bookingsQuantity: 0,
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
