/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  BookingRecapResponseModel,
  BookingRecapResponseStockModel,
  BookingRecapStatus,
  CategoryResponseModel,
  GetIndividualOfferWithAddressResponseModel,
  GetOffererNameResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  GetOfferManagingOffererResponseModel,
  GetOfferStockResponseModel,
  GetOfferVenueResponseModel,
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
  ManagedVenues,
  OfferStatus,
  PriceCategoryResponseModel,
  SubcategoryIdEnum,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
  VenueProviderResponse,
  VenueTypeCode,
} from 'apiClient/v1'
import {
  BookingFormula,
  BookingOfferType,
  GetBookingResponse,
} from 'apiClient/v2'
import { IndividualOfferContextValues } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { REIMBURSEMENT_RULES } from 'commons/core/Finances/constants'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { StocksEvent } from 'components/StocksEventList/StocksEventList'

import { listOffersVenueFactory } from './collectiveApiFactories'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let getOffererNameId = 1
let bookingId = 1
let stockResponseId = 1
let priceCategoryId = 1
let offerCategoryId = 1
let offerSubCategoryId = 1

export const listOffersOfferFactory = (
  customListOffersOffer: Partial<ListOffersOfferResponseModel> = {}
): ListOffersOfferResponseModel => {
  const currentOfferId = offerId++

  return {
    id: currentOfferId,
    status: OfferStatus.ACTIVE,
    subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
    isActive: true,
    isDigital: false,
    hasBookingLimitDatetimesPassed: true,
    isEducational: false,
    name: `offer name ${offerId}`,
    isEvent: true,
    isThing: false,
    isHeadlineOffer: false,
    venue: listOffersVenueFactory(),
    stocks: [],
    isEditable: true,
    ...customListOffersOffer,
  }
}

export const listOffersStockFactory = (
  customListOffersStockFactory: Partial<ListOffersStockResponseModel> = {}
): ListOffersStockResponseModel => {
  const currentStockId = stockId++
  return {
    id: currentStockId,
    hasBookingLimitDatetimePassed: false,
    remainingQuantity: 100,
    ...customListOffersStockFactory,
  }
}

export const getIndividualOfferFactory = (
  customGetIndividualOffer: Partial<GetIndividualOfferWithAddressResponseModel> = {}
): GetIndividualOfferWithAddressResponseModel => {
  const currentOfferId = offerId++

  return {
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isActivable: true,
    isEditable: true,
    isEvent: true,
    isHeadlineOffer: false,
    isThing: true,
    id: currentOfferId,
    status: OfferStatus.ACTIVE,
    venue: getOfferVenueFactory(),
    hasBookingLimitDatetimesPassed: false,
    hasStocks: true,
    dateCreated: '2020-04-12T19:31:12Z',
    isDigital: false,
    isDuo: true,
    isNational: true,
    subcategoryId: SubcategoryIdEnum.SEANCE_CINE,
    lastProvider: null,
    bookingsCount: 0,
    isNonFreeOffer: true,
    visualDisabilityCompliant: true,
    audioDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    hasPendingBookings: false,
    priceCategories: [priceCategoryFactory()],
    eventOpeningHours: null,
    externalTicketOfficeUrl: 'https://chuck.no',
    extraData: {
      author: 'Chuck Norris',
      performer: 'Le Poing de Chuck',
      ean: '1234567891234',
      showType: 'Cinéma',
      showSubType: 'PEGI 18',
      stageDirector: 'JCVD',
      speaker: "Chuck Norris n'a pas besoin de doubleur",
      visa: 'USA',
    },
    ...customGetIndividualOffer,
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

export const getOfferVenueFactory = (
  customGetOfferVenue: Partial<GetOfferVenueResponseModel> = {}
): GetOfferVenueResponseModel => {
  const currentVenueId = venueId++

  return {
    id: currentVenueId,
    street: 'Ma Rue',
    city: 'Ma Ville',
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    postalCode: '11100',
    publicName: 'Mon Lieu',
    departementCode: '78',
    visualDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: true,
    managingOfferer: getOfferManagingOffererFactory(),
    ...customGetOfferVenue,
  }
}

export const getOfferManagingOffererFactory = (
  customGetOfferManagingOfferer: Partial<GetOfferManagingOffererResponseModel> = {}
): GetOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++

  return {
    id: 3,
    name: `Le nom de la structure ${currentOffererId}`,
    allowedOnAdage: true,
    ...customGetOfferManagingOfferer,
  }
}

export const individualOfferContextValuesFactory = (
  customIndividualOfferContextValues: Partial<IndividualOfferContextValues> = {}
): IndividualOfferContextValues => {
  const offer = getIndividualOfferFactory()

  return {
    offer,
    categories: [],
    subCategories: [],
    isEvent: null,
    setIsEvent: () => {},
    ...customIndividualOfferContextValues,
  }
}

export const bookingRecapStockFactory = (
  customBookingRecapStock: Partial<BookingRecapResponseStockModel> = {}
): BookingRecapResponseStockModel => {
  const offer = getIndividualOfferFactory()

  return {
    offerId: offer.id,
    offerName: offer.name,
    offerIsEducational: false,
    offerIsbn: '123456789',
    ...customBookingRecapStock,
  }
}
export const bookingRecapFactory = (
  customBookingRecap: Partial<BookingRecapResponseModel> = {}
): BookingRecapResponseModel => {
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
    bookingStatus: BookingRecapStatus.BOOKED,
    bookingStatusHistory: [
      {
        date: '2020-04-12T19:31:12Z',
        status: BookingRecapStatus.BOOKED,
      },
    ],
    bookingToken: `TOKEN${bookingId++}`,
    stock: bookingRecapStockFactory(),
    ...customBookingRecap,
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
    managingOffererId: 1,
    offererName: 'la structure de Michel',
    visualDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: true,
    isPermanent: true,
    ...customVenueListItem,
  }
}

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
  canBeWithdrawable: false,
  onlineOfflinePlatform: CATEGORY_STATUS.ONLINE,
  reimbursementRule: REIMBURSEMENT_RULES.STANDARD,
  isSelectable: true,
  canExpire: true,
  canHaveOpeningHours: false,
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

export function getOffererNameFactory(
  customGetOfferer: Partial<GetOffererNameResponseModel> = {}
): GetOffererNameResponseModel {
  return {
    id: getOffererNameId++,
    name: 'Ma super structure',
    allowedOnAdage: true,
    ...customGetOfferer,
  }
}

export const defaultGetOffererResponseModel: GetOffererResponseModel = {
  apiKey: {
    maxAllowed: 10,
    prefixes: [],
  },
  city: 'Fake City',
  dateCreated: '2022-01-01T00:00:00Z',
  hasAvailablePricingPoints: false,
  hasDigitalVenueAtLeastOneOffer: false,
  hasValidBankAccount: true,
  hasPendingBankAccount: false,
  hasNonFreeOffer: true,
  hasActiveOffer: true,
  hasBankAccountWithPendingCorrections: false,
  hasHeadlineOffer: false,
  venuesWithNonFreeOffersWithoutBankAccounts: [],
  isActive: false,
  isValidated: false,
  managedVenues: [],
  siren: '123456789',
  name: 'Ma super structure',
  id: 1,
  postalCode: '00000',
  street: 'Fake Address',
  allowedOnAdage: true,
  isOnboarded: true,
  hasPartnerPage: false,
}

export const defaultGetOffererVenueResponseModel: GetOffererVenueResponseModel =
  {
    collectiveDmsApplications: [],
    hasAdageId: false,
    hasCreatedOffer: false,
    isVirtual: false,
    isVisibleInApp: true,
    name: 'Mon super lieu',
    id: 1,
    venueTypeCode: VenueTypeCode.LIEU_ADMINISTRATIF,
    hasVenueProviders: false,
    isPermanent: true,
    bannerUrl: null,
    bannerMeta: null,
    hasPartnerPage: true,
  }

export const defaultGetBookingResponse: GetBookingResponse = {
  bookingId: 'test_booking_id',
  dateOfBirth: '1980-02-01T20:00:00Z',
  email: 'test@email.com',
  formula: BookingFormula.PLACE,
  isUsed: false,
  offerId: 12345,
  offerType: BookingOfferType.EVENEMENT,
  phoneNumber: '0100000000',
  publicOfferId: 'test_public_offer_id',
  theater: { theater_any: 'theater_any' },
  venueAddress: null,
  venueName: 'mon lieu',
  datetime: '2001-02-01T20:00:00Z',
  ean13: 'test ean113',
  offerName: 'Nom de la structure',
  price: 13,
  quantity: 1,
  userName: 'USER',
  firstName: 'john',
  lastName: 'doe',
  venueDepartmentCode: '75',
  priceCategoryLabel: 'price label',
}

export const defaultBankAccount: BankAccountResponseModel = {
  bic: 'CCOPFRPP',
  dateCreated: '2020-05-07',
  dsApplicationId: 1,
  id: 1,
  isActive: true,
  label: 'Mon compte bancaire',
  linkedVenues: [
    {
      commonName: 'Mon super lieu',
      id: 1,
    },
  ],
  obfuscatedIban: 'XXXX-123',
  status: BankAccountApplicationStatus.ACCEPTE,
}

export const defaultManagedVenues: ManagedVenues = {
  commonName: 'Mon super lieu',
  name: 'RAISON SOCIALE',
  id: 1,
  siret: '123456789',
  hasPricingPoint: true,
}

export const defaultVenueProvider: VenueProviderResponse = {
  id: 1,
  isActive: true,
  isFromAllocineProvider: false,
  lastSyncDate: undefined,
  venueId: 2,
  dateCreated: '2021-08-15T00:00:00Z',
  venueIdAtOfferProvider: 'cdsdemorc1',
  provider: {
    name: 'Ciné Office',
    id: 12,
    hasOffererProvider: false,
    isActive: true,
  },
  quantity: 0,
  isDuo: true,
  price: 0,
}
