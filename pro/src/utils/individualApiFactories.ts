/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import {
  CategoryResponseModel,
  GetOfferStockResponseModel,
  GetVenueResponseModel,
  PriceCategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'
import { IndividualOfferContextValues } from 'context/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'core/Finances'
import { CATEGORY_STATUS } from 'core/Offers/constants'
import { IndividualOfferVenueItem } from 'core/Venue/types'

import { getIndividualOfferFactory } from './apiFactories'

let stockId = 1
let stockResponseId = 1
let venueId = 1
let priceCategoryId = 1
let offerCategoryId = 1
let offerSubCategoryId = 1

export const individualOfferVenueItemFactory = (
  customIndividualOfferVenueItem: Partial<IndividualOfferVenueItem> = {}
): IndividualOfferVenueItem => {
  return {
    ...venueListItemFactory(),
    ...customIndividualOfferVenueItem,
  }
}

export const getVenueFactory = (
  customGetVenue: Partial<GetVenueResponseModel> = {}
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
    timezone: 'Europe/Paris',
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
    hasAdageId: false,
    venueTypeCode: VenueTypeCode.AUTRE,
    ...customGetVenue,
  }
}

export const venueListItemFactory = (
  customVenueListItem: Partial<VenueListItemResponseModel> = {}
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
    visualDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: true,
    ...customVenueListItem,
  }
}

export const priceCategoryFactory = (
  customPriceCategory: Partial<PriceCategoryResponseModel> = {}
): PriceCategoryResponseModel => ({
  id: priceCategoryId++,
  label: 'mon label',
  price: 66.6,
  ...customPriceCategory,
})

export const categoryFactory = (
  customCategory: Partial<CategoryResponseModel> = {}
): CategoryResponseModel => ({
  id: String(offerCategoryId++),
  proLabel: `catégorie ${offerCategoryId}`,
  isSelectable: true,
  ...customCategory,
})

export const subcategoryFactory = (
  customSubcategory: Partial<SubcategoryResponseModel> = {}
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
  ...customSubcategory,
})

export const StocksEventFactory = (
  customStocksEvent: Partial<StocksEvent> = {}
): StocksEvent => {
  return {
    id: stockId++,
    beginningDatetime: '2021-10-15T12:00:00.000Z',
    bookingLimitDatetime: '2021-09-15T12:00:00.000Z',
    priceCategoryId: 2,
    quantity: 18,
    bookingsQuantity: 0,
    isEventDeletable: true,
    ...customStocksEvent,
  }
}

export const getOfferStockFactory = (
  customGetOfferStock: Partial<GetOfferStockResponseModel> = {}
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
    ...customGetOfferStock,
  }
}

export const individualOfferContextValuesFactory = (
  customIndividualOfferContextValues: Partial<IndividualOfferContextValues> = {}
): IndividualOfferContextValues => {
  const offer = getIndividualOfferFactory()

  return {
    offerId: offer.id,
    offer,
    venueList: [],
    offererNames: [],
    categories: [],
    subCategories: [],
    setSubcategory: () => {},
    showVenuePopin: {},
    ...customIndividualOfferContextValues,
  }
}
