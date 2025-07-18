/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { add, addDays } from 'date-fns'

import { EacFormat } from 'apiClient/adage'
import {
  CollectiveBookingBankAccountStatus,
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
  GetVenueResponseModel,
  OfferAddressType,
  StudentLevels,
  VenueTypeCode,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
  CollectiveOfferDisplayedStatus,
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  GetCollectiveOfferBookingResponseModel,
  CollectiveBookingStatus,
} from 'apiClient/v1'
import { BOOKING_STATUS } from 'commons/core/Bookings/constants'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let bookingId = 1
let offerBookingId = 1
let bookingDetailsId = 1
let institutionId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<CollectiveOfferResponseModel> = {}
): CollectiveOfferResponseModel => {
  const currentId = offerId++

  return {
    id: currentId,
    displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: true,
    name: `offer name ${offerId}`,
    venue: listOffersVenueFactory(),
    stocks: [
      {
        hasBookingLimitDatetimePassed: false,
        remainingQuantity: 1,
        startDatetime: new Date().toISOString(),
      },
    ],
    isPublicApi: false,
    interventionArea: [],
    isShowcase: false,
    allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
    ...customCollectiveOffer,
    formats: [EacFormat.ATELIER_DE_PRATIQUE],
  }
}
export const listOffersVenueFactory = (
  customListOffersVenue: Partial<ListOffersVenueResponseModel> = {}
): ListOffersVenueResponseModel => ({
  id: 1,
  name: 'venue name',
  offererName: 'offerer name',
  isVirtual: false,
  ...customListOffersVenue,
})

const sharedCollectiveOfferData = {
  isActive: true,
  displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
  isCancellable: true,
  isTemplate: true,
  allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
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
  provider: null,
  formats: [EacFormat.ATELIER_DE_PRATIQUE],
}

export const getCollectiveOfferFactory = (
  customCollectiveOffer: Partial<GetCollectiveOfferResponseModel> = {}
): GetCollectiveOfferResponseModel => {
  const currentOfferId = offerId++
  return {
    ...sharedCollectiveOfferData,
    id: currentOfferId,
    venue: getCollectiveOfferVenueFactory(),
    isBookable: true,
    isTemplate: false,
    allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
    collectiveStock: getCollectiveOfferCollectiveStockFactory(),
    location: {
      locationType: CollectiveLocationType.ADDRESS,
    },
    history: {
      future: [
        CollectiveOfferDisplayedStatus.BOOKED,
        CollectiveOfferDisplayedStatus.ENDED,
        CollectiveOfferDisplayedStatus.REIMBURSED,
      ],
      past: [
        {
          status: CollectiveOfferDisplayedStatus.PUBLISHED,
          datetime: '2025-07-05T13:38:12.020421Z',
        },
        {
          status: CollectiveOfferDisplayedStatus.PREBOOKED,
          datetime: '2025-06-23T13:28:11.883708Z',
        },
        {
          status: CollectiveOfferDisplayedStatus.EXPIRED,
          datetime: '2025-06-24T13:28:11.883708Z',
        },
      ],
    },
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
    startDatetime: add(Date.now(), { days: 2 }).toISOString(),
    endDatetime: add(Date.now(), { days: 3 }).toISOString(),
    bookingLimitDatetime: add(Date.now(), { days: 1 }).toISOString(),
    isBooked: false,
    isCancellable: false,
    ...customGetCollectiveOfferCollectiveStock,
  }
}

export const getCollectiveOfferBookingFactory = (
  customGetCollectiveOfferBooking: Partial<GetCollectiveOfferBookingResponseModel> = {}
): GetCollectiveOfferBookingResponseModel => {
  const currentBookingId = offerBookingId++
  return {
    id: currentBookingId,
    status: CollectiveBookingStatus.CONFIRMED,
    dateCreated: new Date().toISOString(),
    cancellationLimitDate: add(Date.now(), { days: 1 }).toISOString(),
    confirmationLimitDate: add(Date.now(), { days: 1 }).toISOString(),
    ...customGetCollectiveOfferBooking,
  }
}

export const getCollectiveOfferTemplateFactory = (
  customCollectiveOfferTemplate: Partial<GetCollectiveOfferTemplateResponseModel> = {}
): GetCollectiveOfferTemplateResponseModel => ({
  ...sharedCollectiveOfferData,
  id: offerId++,
  venue: getCollectiveOfferVenueFactory(),
  isTemplate: true,
  dates: {
    start: new Date().toISOString(),
    end: addDays(new Date(), 1).toISOString(),
  },
  ...customCollectiveOfferTemplate,
})

export const getCollectiveOfferVenueFactory = (
  customGetCollectiveOfferVenue: Partial<GetCollectiveOfferVenueResponseModel> = {}
): GetCollectiveOfferVenueResponseModel => {
  const currentVenueId = venueId++
  return {
    name: `Le nom du lieu ${currentVenueId}`,
    managingOfferer: getCollectiveOfferManagingOffererFactory(),
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
    siren: '123456789',
    allowedOnAdage: true,
    ...customGetCollectiveOfferManagingOfferer,
  }
}

export const collectiveBookingCollectiveStockFactory = (
  customCollectiveBookingCollectiveStock: Partial<CollectiveBookingCollectiveStockResponseModel> = {}
): CollectiveBookingCollectiveStockResponseModel => ({
  bookingLimitDatetime: new Date().toISOString(),
  eventStartDatetime: new Date().toISOString(),
  eventEndDatetime: new Date().toISOString(),
  numberOfTickets: 1,
  offerId: 1,
  offerIsEducational: true,
  offerEan: null,
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

export const collectiveBookingByIdFactory = (
  customCollectiveBookingById?: Partial<CollectiveBookingByIdResponseModel>
): CollectiveBookingByIdResponseModel => {
  const currentBookingDetailsId = bookingDetailsId++
  return {
    bankAccountStatus: CollectiveBookingBankAccountStatus.ACCEPTED,
    startDatetime: new Date().toISOString(),
    endDatetime: new Date().toISOString(),
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
  id: 1,
  audioDisabilityCompliant: false,
  collectiveDmsApplications: [],
  collectiveDomains: [],
  dateCreated: new Date().toISOString(),
  dmsToken: 'fakeDmsToken',
  hasAdageId: true,
  hasOffers: true,
  hasActiveIndividualOffer: true,
  isOpenToPublic: true,
  isVirtual: false,
  managingOfferer: {
    id: 1,
    city: 'Paris',
    dateCreated: new Date().toISOString(),
    isValidated: true,
    name: 'Ma super structure',
    postalCode: '75000',
    siren: '',
    allowedOnAdage: true,
  },
  mentalDisabilityCompliant: true,
  motorDisabilityCompliant: false,
  name: 'Lieu de test',
  timezone: 'Europe/Paris',
  venueTypeCode: VenueTypeCode.CENTRE_CULTUREL,
  visualDisabilityCompliant: true,
  openingHours: null,
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
