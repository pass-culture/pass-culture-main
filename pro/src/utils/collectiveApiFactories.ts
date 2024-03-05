/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { addDays } from 'date-fns'

import { EacFormat } from 'apiClient/adage'
import {
  CollectiveBookingBankInformationStatus,
  CollectiveBookingByIdResponseModel,
  CollectiveBookingCollectiveStockResponseModel,
  CollectiveBookingResponseModel,
  DMSApplicationForEAC,
  DMSApplicationstatus,
  EducationalInstitutionResponseModel,
  EducationalRedactorResponseModel,
  GetCollectiveOfferCollectiveStockResponseModel,
  GetCollectiveOfferManagingOffererResponseModel,
  GetCollectiveOfferRequestResponseModel,
  GetCollectiveOfferVenueResponseModel,
  GetCollectiveVenueResponseModel,
  GetVenueResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  VenueTypeCode,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from 'apiClient/v1'
import { BOOKING_STATUS } from 'core/Bookings/constants'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let bookingId = 1
let bookingDetailsId = 1
let institutionId = 1

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
  isPublicApi: false,
  id: 123,
  offerVenue: {
    venueId: null,
    otherAddress: 'A la mairie',
    addressType: OfferAddressType.OTHER,
  },
  students: [StudentLevels.COLL_GE_3E],
  venueId: 'VENUE_ID',
  imageUrl: 'https://example.com/image.jpg',
  imageCredit: 'image credit',
  nationalProgram: {
    id: 1,
    name: 'Collège au cinéma',
  },
  formats: [EacFormat.ATELIER_DE_PRATIQUE],
}

// TODO factories: remove customStock & customVenue as an argument
export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<GetCollectiveOfferResponseModel> = {},
  customStock: GetCollectiveOfferCollectiveStockResponseModel = getCollectiveOfferCollectiveStockFactory() ||
    null,
  customVenue: GetCollectiveOfferVenueResponseModel = getCollectiveOfferVenueFactory()
): GetCollectiveOfferResponseModel => {
  const stock = customStock === null ? null : customStock
  const currentOfferId = offerId++
  return {
    ...sharedCollectiveOfferData,
    id: currentOfferId,
    venue: customVenue,
    isBookable: true,
    isVisibilityEditable: true,
    isTemplate: false,
    collectiveStock: stock,
    ...customCollectiveOffer,
  }
}

export const getCollectiveOfferCollectiveStockFactory = (
  customGetCollectiveOfferCollectiveStock: Partial<GetCollectiveOfferCollectiveStockResponseModel> = {}
): GetCollectiveOfferCollectiveStockResponseModel => {
  const currentStockId = stockId++
  return {
    id: currentStockId,
    price: 100,
    beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2021-09-15T12:00:00Z').toISOString(),
    isBooked: false,
    isCancellable: false,
    isEducationalStockEditable: true,
    ...customGetCollectiveOfferCollectiveStock,
  }
}

// TODO factories: remove customVenue as an argument
export const collectiveOfferTemplateFactory = (
  customCollectiveOfferTemplate: Partial<GetCollectiveOfferTemplateResponseModel> = {},
  customVenue: GetCollectiveOfferVenueResponseModel = getCollectiveOfferVenueFactory()
): GetCollectiveOfferTemplateResponseModel => ({
  ...sharedCollectiveOfferData,
  id: offerId++,
  venue: customVenue,
  isTemplate: true,
  dates: {
    start: new Date().toISOString(),
    end: addDays(new Date(), 1).toISOString(),
  },
  ...customCollectiveOfferTemplate,
})

// TODO factories: remove customOfferer as an argument
export const getCollectiveOfferVenueFactory = (
  customGetCollectiveOfferVenue: Partial<GetCollectiveOfferVenueResponseModel> = {},
  customOfferer: GetCollectiveOfferManagingOffererResponseModel = getCollectiveOfferManagingOffererFactory()
): GetCollectiveOfferVenueResponseModel => {
  const currentVenueId = venueId++
  return {
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: customOfferer,
    publicName: 'Mon Lieu',
    id: currentVenueId,
    departementCode: '973',
    ...customGetCollectiveOfferVenue,
  }
}

export const getCollectiveOfferManagingOffererFactory = (
  customGetCollectiveOfferManagingOfferer: Partial<GetCollectiveOfferManagingOffererResponseModel> = {}
): GetCollectiveOfferManagingOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    id: currentOffererId,
    name: `La nom de la structure ${currentOffererId}`,
    ...customGetCollectiveOfferManagingOfferer,
  }
}

export const collectiveBookingCollectiveStockFactory = (
  customCollectiveBookingCollectiveStock: Partial<CollectiveBookingCollectiveStockResponseModel> = {}
): CollectiveBookingCollectiveStockResponseModel => ({
  bookingLimitDatetime: new Date().toISOString(),
  eventBeginningDatetime: new Date().toISOString(),
  numberOfTickets: 1,
  offerId: 1,
  offerIsEducational: true,
  offerIsbn: null,
  offerName: 'ma super offre collective',
  ...customCollectiveBookingCollectiveStock,
})

export const collectiveBookingFactory = (
  customCollectiveBooking: Partial<CollectiveBookingResponseModel> = {}
): CollectiveBookingResponseModel => {
  const currentBookingId = bookingId++
  return {
    bookingAmount: 1,
    bookingCancellationLimitDate: new Date().toISOString(),
    bookingConfirmationDate: new Date().toISOString(),
    bookingConfirmationLimitDate: new Date().toISOString(),
    bookingDate: new Date().toISOString(),
    bookingId: currentBookingId.toString(),
    bookingIsDuo: false,
    bookingStatus: BOOKING_STATUS.PENDING,
    bookingStatusHistory: [
      { date: new Date().toISOString(), status: BOOKING_STATUS.PENDING },
    ],
    bookingToken: null,
    institution: {
      city: 'PARIS',
      id: 1,
      institutionId: '1',
      institutionType: null,
      name: 'COLLEGE DE PARIS',
      postalCode: '75001',
      phoneNumber: '0601020304',
    },
    stock: collectiveBookingCollectiveStockFactory(),
    ...customCollectiveBooking,
  }
}

// TODO factories: type this
export const defaultCollectiveBookingStock = {
  bookingLimitDatetime: new Date().toISOString(),
  eventBeginningDatetime: new Date().toISOString(),
  numberOfTickets: 1,
  offerIdentifier: '1',
  offerId: 1,
  offerIsEducational: true,
  offerIsbn: null,
  offerName: 'ma super offre collective',
}

export const collectiveBookingByIdFactory = (
  customCollectiveBookingById?: Partial<CollectiveBookingByIdResponseModel>
): CollectiveBookingByIdResponseModel => {
  const currentBookingDetailsId = bookingDetailsId++
  return {
    bankInformationStatus: CollectiveBookingBankInformationStatus.ACCEPTED,
    bankAccountStatus: null,
    beginningDatetime: new Date().toISOString(),
    educationalInstitution: {
      city: 'Paris',
      id: 1,
      institutionId: '1',
      institutionType: 'LYCEE',
      name: 'De Paris',
      phoneNumber: '0601020304',
      postalCode: '75000',
    },
    educationalRedactor: {
      civility: 'Mr',
      email: 'test@example.com',
      firstName: 'Jean',
      id: 1,
      lastName: 'Dupont',
    },
    id: currentBookingDetailsId,
    isCancellable: true,
    numberOfTickets: 1,
    offerVenue: {
      addressType: OfferAddressType.SCHOOL,
      otherAddress: '',
      venueId: 1,
    },
    offererId: 1,
    price: 100,
    students: [StudentLevels.LYC_E_SECONDE],
    venueDMSApplicationId: 1,
    venueId: 1,
    venuePostalCode: '75000',
    ...customCollectiveBookingById,
  }
}

export const getCollectiveVenueFactory = (
  customGetCollectiveVenue: Partial<GetCollectiveVenueResponseModel> = {}
): GetCollectiveVenueResponseModel => {
  return {
    collectiveDomains: [],
    collectiveDescription: '',
    collectiveEmail: '',
    collectiveInterventionArea: [],
    collectiveLegalStatus: null,
    collectiveNetwork: [],
    collectivePhone: '',
    collectiveStudents: [],
    collectiveWebsite: '',
    siret: '1234567890',
    ...customGetCollectiveVenue,
  }
}

export const defaultEducationalInstitution: EducationalInstitutionResponseModel =
  {
    city: 'Paris',
    id: institutionId++,
    institutionId: 'ABC123',
    institutionType: 'LYCEE',
    name: 'Sacré coeur',
    phoneNumber: '0601020304',
    postalCode: '75000',
  }

export const defaultEducationalRedactor: EducationalRedactorResponseModel = {
  civility: 'Mr',
  email: 'Jean.Dupont@example.com',
  firstName: 'Jean',
  lastName: 'Dupont',
}

export const defaultDMSApplicationForEAC: DMSApplicationForEAC = {
  application: 123,
  depositDate: new Date().toISOString(),
  lastChangeDate: new Date().toISOString(),
  procedure: 456,
  state: DMSApplicationstatus.EN_CONSTRUCTION,
  venueId: 1,
}

export const defaultGetVenue: GetVenueResponseModel = {
  dateCreated: new Date().toISOString(),
  dmsToken: 'fakeDmsToken',
  hasAdageId: true,
  collectiveDmsApplications: [],
  isVirtual: false,
  collectiveDomains: [],
  managingOfferer: {
    city: 'Paris',
    dateCreated: new Date().toISOString(),
    isValidated: true,
    name: 'Ma super structure',
    id: 1,
    postalCode: '75000',
    siren: '',
  },
  mentalDisabilityCompliant: null,
  motorDisabilityCompliant: null,
  name: 'Lieu de test',
  id: 1,
  venueTypeCode: VenueTypeCode.CENTRE_CULTUREL,
  timezone: 'Europe/Paris',
}

export const defaultGetCollectiveOfferRequest: GetCollectiveOfferRequestResponseModel =
  {
    comment: 'comment',
    institution: {
      city: 'Paris',
      institutionId: 'ABC123',
      institutionType: 'LYCEE',
      name: 'Sacré coeur',
      postalCode: '75000',
    },
    redactor: {
      email: 'Jean.Dupont@example.com',
      firstName: 'Jean',
      lastName: 'Dupont',
    },
  }

// TODO factories: type this
export const defaultCollectifOfferResponseModel = {
  isActive: true,
  offerId: 1,
  bookingEmails: [],
  name: 'mon offre',
  contactEmail: 'mail@example.com',
  contactPhone: '0600000000',
  dateCreated: 'date',
  description: 'description',
  domains: [],
  hasBookingLimitDatetimesPassed: false,
  interventionArea: [],
  isCancellable: true,
  isEditable: true,
  id: 1,
  offerVenue: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: 12,
  },
  status: OfferStatus.ACTIVE,
  students: [],
  venue: {
    isVirtual: false,
    id: 1,
    managingOfferer: {
      city: 'Vélizy',
      id: 1,
      dateCreated: 'date',
      isActive: true,
      isValidated: true,
      name: 'mon offerer',
      postalCode: '78sang40',
      thumbCount: 1,
    },
    managingOffererId: 'A1',
    name: 'mon lieu',
    thumbCount: 1,
  },
  venueId: 'A1',
}
