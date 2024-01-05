/* istanbul ignore file */
import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  BookingRecapResponseModel,
  type CollectiveOfferOfferVenueResponseModel,
  type GetCollectiveOfferManagingOffererResponseModel,
  GetCollectiveOfferResponseModel,
  type GetCollectiveOfferVenueResponseModel,
  GetIndividualOfferResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  GetOfferManagingOffererResponseModel,
  GetOfferVenueResponseModel,
  ListOffersOfferResponseModel,
  ListOffersStockResponseModel,
  ListOffersVenueResponseModel,
  ManagedVenues,
  OfferAddressType,
  OfferStatus,
  SubcategoryIdEnum,
  VenueListItemResponseModel,
  VenueTypeCode,
} from 'apiClient/v1'
import { BookingRecapStatus } from 'apiClient/v1/models/BookingRecapStatus'
import {
  BookingFormula,
  BookingOfferType,
  GetBookingResponse,
} from 'apiClient/v2'

let offerId = 1
let venueId = 1
let offererId = 1
let stockId = 1
let bookingId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer = {},
  customStock = collectiveStockFactory() || null,
  customVenue = offerVenueFactory()
) => {
  const stocks = customStock === null ? [] : [customStock]
  const currentOfferId = offerId++

  return {
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isEditable: true,
    isEvent: true,
    isFullyBooked: false,
    isThing: false,
    id: currentOfferId,
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
  customOffer: Partial<GetIndividualOfferResponseModel> = {}
): GetIndividualOfferResponseModel => {
  const currentOfferId = offerId++

  return {
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isActivable: true,
    isEditable: true,
    isEvent: false,
    isThing: true,
    id: currentOfferId,
    status: OfferStatus.ACTIVE,
    venue: offerVenueFactory(),
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
    ...customOffer,
  }
}

export const getVenueListItemFactory = (
  customVenue = {},
  customOfferer = offererFactory()
): VenueListItemResponseModel => {
  const currentVenueId = venueId++
  return {
    id: currentVenueId,
    isVirtual: false,
    name: `Le nom du lieu ${currentVenueId}`,
    managingOffererId: customOfferer.id,
    publicName: 'Mon Lieu',
    hasCreatedOffer: true,
    hasMissingReimbursementPoint: true,
    offererName: 'offerer',
    venueTypeCode: VenueTypeCode.AUTRE,
    ...customVenue,
  }
}

export const offererFactory = (
  customOfferer = {}
): GetOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++

  return {
    id: 3,
    name: `Le nom de la structure ${currentOffererId}`,
    ...customOfferer,
  }
}

export const offerVenueFactory = (
  customVenue: Partial<GetOfferVenueResponseModel> = {},
  customOfferer: GetOfferManagingOffererResponseModel = offererFactory()
): GetOfferVenueResponseModel => {
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
    visualDisabilityCompliant: true,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    audioDisabilityCompliant: true,
    managingOfferer: customOfferer,
    ...customVenue,
  }
}

export const bookingRecapFactory = (
  customBookingRecap = {},
  customOffer = {}
): BookingRecapResponseModel => {
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
    bookingStatus: BookingRecapStatus.BOOKED,
    bookingStatusHistory: [
      {
        date: '2020-04-12T19:31:12Z',
        status: BookingRecapStatus.BOOKED,
      },
    ],
    bookingToken: `TOKEN${bookingId++}`,
    stock: {
      offerId: offer.id,
      offerName: offer.name,
      offerIsEducational: false,
      stockIdentifier: 1234,
      offerIsbn: '123456789',
    },
    ...customBookingRecap,
  }
}

export const defaultGetOffererResponseModel: GetOffererResponseModel = {
  address: 'Fake Address',
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
  venuesWithNonFreeOffersWithoutBankAccounts: [],
  isActive: false,
  isValidated: false,
  managedVenues: [],
  name: 'Ma super structure',
  id: 1,
  postalCode: '00000',
}

export const defaultGetOffererVenueResponseModel: GetOffererVenueResponseModel =
  {
    collectiveDmsApplications: [],
    hasAdageId: false,
    hasCreatedOffer: false,
    hasMissingReimbursementPoint: false,
    isVirtual: false,
    name: 'Mon super lieu',
    id: 0,
    venueTypeCode: VenueTypeCode.LIEU_ADMINISTRATIF,
    hasVenueProviders: false,
    isPermanent: true,
    bannerUrl: null,
    bannerMeta: null,
  }

export const defaultBookingResponse: GetBookingResponse = {
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

type ListOffersOfferResponseModelFactory = {
  customOffer?: Partial<ListOffersOfferResponseModel>
  customStocksList?: ListOffersStockResponseModel[]
  customVenue?: Partial<ListOffersVenueResponseModel>
}

export const listOffersOfferResponseModelFactory = ({
  customOffer,
  customStocksList,
  customVenue,
}: ListOffersOfferResponseModelFactory = {}): ListOffersOfferResponseModel => ({
  hasBookingLimitDatetimesPassed: true,
  id: offerId++,
  isActive: true,
  isEditable: true,
  isEducational: false,
  isEvent: true,
  isShowcase: false,
  isThing: false,
  name: `mon offre ${offerId}`,
  productIsbn: null,
  status: OfferStatus.ACTIVE,
  stocks: customStocksList ?? [listOffersStockResponseModelFactory()],
  subcategoryId: SubcategoryIdEnum.CINE_PLEIN_AIR,
  thumbUrl: 'https://www.example.com',
  venue: listOffersVenueResponseModelFactory(customVenue),
  ...customOffer,
})

const listOffersStockResponseModelFactory = (
  customStock?: Partial<ListOffersStockResponseModel>
): ListOffersStockResponseModel => ({
  id: stockId++,
  hasBookingLimitDatetimePassed: false,
  remainingQuantity: 10,
  ...customStock,
})

const listOffersVenueResponseModelFactory = (
  customVenue?: Partial<ListOffersVenueResponseModel>
): ListOffersVenueResponseModel => ({
  id: venueId++,
  name: 'mon lieu azmefhzihfmiùazer',
  isVirtual: false,
  offererName: 'mon offerer',
  departementCode: '75',
  ...customVenue,
})

export const defaultBankAccountResponseModel: BankAccountResponseModel = {
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
  id: 1,
  siret: '123456789',
  hasPricingPoint: true,
}

const defaultCollectiveOfferOfferVenueResponseModel: CollectiveOfferOfferVenueResponseModel =
  {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: 'other',
  }

const defaultGetCollectiveOfferManagingOffererResponseModel: GetCollectiveOfferManagingOffererResponseModel =
  {
    id: 1,
    name: 'nom',
  }

const defaultGetCollectiveOfferVenueResponseModel: GetCollectiveOfferVenueResponseModel =
  {
    id: 1,
    managingOfferer: defaultGetCollectiveOfferManagingOffererResponseModel,
    name: 'nom',
  }

export const defaultGetCollectiveOfferResponseModel: GetCollectiveOfferResponseModel =
  {
    bookingEmails: [],
    contactEmail: 'contact@contact.contact',
    dateCreated: '10/18/2000',
    description: 'description',
    domains: [],
    hasBookingLimitDatetimesPassed: false,
    id: 1,
    interventionArea: [],
    isActive: false,
    isBookable: false,
    isCancellable: false,
    isEditable: false,
    isPublicApi: false,
    isVisibilityEditable: false,
    name: 'offre',
    offerVenue: defaultCollectiveOfferOfferVenueResponseModel,
    status: OfferStatus.ACTIVE,
    students: [],
    venue: defaultGetCollectiveOfferVenueResponseModel,
  }
