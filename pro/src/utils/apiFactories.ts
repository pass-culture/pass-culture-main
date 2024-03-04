/* istanbul ignore file */
import {
  BankAccountApplicationStatus,
  BankAccountResponseModel,
  BookingRecapResponseModel,
  GetCollectiveOfferResponseModel,
  GetIndividualOfferResponseModel,
  GetOfferManagingOffererResponseModel,
  GetOfferVenueResponseModel,
  GetOffererResponseModel,
  GetOffererVenueResponseModel,
  ManagedVenues,
  OfferAddressType,
  OfferStatus,
  SubcategoryIdEnum,
  VenueTypeCode,
  type CollectiveOfferOfferVenueResponseModel,
  type GetCollectiveOfferManagingOffererResponseModel,
  type GetCollectiveOfferVenueResponseModel,
} from 'apiClient/v1'
import { BookingRecapStatus } from 'apiClient/v1/models/BookingRecapStatus'
import {
  BookingFormula,
  BookingOfferType,
  GetBookingResponse,
} from 'apiClient/v2'

import { priceCategoryFactory } from './individualApiFactories'

let offerId = 1
let venueId = 1
let offererId = 1
let bookingId = 1

export const getIndividualOfferFactory = (
  customGetIndividualOffer: Partial<GetIndividualOfferResponseModel> = {}
): GetIndividualOfferResponseModel => {
  const currentOfferId = offerId++

  return {
    name: `Le nom de l’offre ${currentOfferId}`,
    isActive: true,
    isActivable: true,
    isEditable: true,
    isEvent: true,
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
    priceCategories: [priceCategoryFactory()],
    extraData: {
      author: 'Chuck Norris',
      performer: 'Le Poing de Chuck',
      ean: 'Chuck n’est pas identifiable par un EAN',
      showType: 'Cinéma',
      showSubType: 'PEGI 18',
      stageDirector: 'JCVD',
      speaker: "Chuck Norris n'a pas besoin de doubleur",
      visa: 'USA',
    },
    ...customGetIndividualOffer,
  }
}

export const getOfferManagingOffererFactory = (
  customGetOfferManagingOfferer: Partial<GetOfferManagingOffererResponseModel> = {}
): GetOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++

  return {
    id: 3,
    name: `Le nom de la structure ${currentOffererId}`,
    ...customGetOfferManagingOfferer,
  }
}

export const getOfferVenueFactory = (
  customGetOfferVenue: Partial<GetOfferVenueResponseModel> = {}
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
    managingOfferer: getOfferManagingOffererFactory(),
    ...customGetOfferVenue,
  }
}

// TODO factories: should remove customOffer as an argument
export const bookingRecapFactory = (
  customBookingRecap = {},
  customOffer = {}
): BookingRecapResponseModel => {
  const offer = getIndividualOfferFactory(customOffer)

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
  hasActiveOffer: true,
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
    isVisibleInApp: true,
    name: 'Mon super lieu',
    id: 0,
    venueTypeCode: VenueTypeCode.LIEU_ADMINISTRATIF,
    hasVenueProviders: false,
    isPermanent: true,
    bannerUrl: null,
    bannerMeta: null,
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
  id: 1,
  siret: '123456789',
  hasPricingPoint: true,
}

const defaultCollectiveOfferOfferVenue: CollectiveOfferOfferVenueResponseModel =
  {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: 'other',
  }

const defaultGetCollectiveOfferManagingOfferer: GetCollectiveOfferManagingOffererResponseModel =
  {
    id: 1,
    name: 'nom',
  }

const defaultGetCollectiveOfferVenue: GetCollectiveOfferVenueResponseModel = {
  id: 1,
  managingOfferer: defaultGetCollectiveOfferManagingOfferer,
  name: 'nom',
}

export const defaultGetCollectiveOffer: GetCollectiveOfferResponseModel = {
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
  offerVenue: defaultCollectiveOfferOfferVenue,
  status: OfferStatus.ACTIVE,
  students: [],
  venue: defaultGetCollectiveOfferVenue,
}
