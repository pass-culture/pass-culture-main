/* istanbul ignore file: Those are test helpers, their coverage is not relevant */

import { add, addDays } from 'date-fns'

import { EacFormat } from '@/apiClient/adage'
import {
  CollectiveBookingStatus,
  CollectiveLocationType,
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  type CollectiveOfferTemplateResponseModel,
  type DMSApplicationForEAC,
  DMSApplicationstatus,
  type EducationalInstitutionResponseModel,
  type EducationalRedactorResponseModel,
  type GetCollectiveOfferBookingResponseModel,
  type GetCollectiveOfferCollectiveStockResponseModel,
  type GetCollectiveOfferManagingOffererResponseModel,
  type GetCollectiveOfferRequestResponseModel,
  type GetCollectiveOfferResponseModel,
  type GetCollectiveOfferTemplateResponseModel,
  type GetCollectiveOfferVenueResponseModel,
  type GetVenueResponseModel,
  type ListOffersVenueResponseModel,
  StudentLevels,
  VenueTypeCode,
} from '@/apiClient/v1'

let offerId = 1
let stockId = 1
let venueId = 1
let offererId = 1
let offerBookingId = 1
let institutionId = 1
let offerTemplateId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<CollectiveOfferResponseModel> = {}
): CollectiveOfferResponseModel => {
  const currentId = offerId++

  return {
    id: currentId,
    displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    name: `offer name ${offerId}`,
    venue: listOffersVenueFactory(),
    stock: {
      bookingLimitDatetime: add(Date.now(), { days: 1 }).toISOString(),
      numberOfTickets: 10,
      price: 10,
    },
    allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
    location: {
      locationType: CollectiveLocationType.SCHOOL,
      location: null,
      locationComment: null,
    },
    ...customCollectiveOffer,
  }
}

export const collectiveOfferTemplateFactory = (
  customCollectiveOfferTemplate: Partial<CollectiveOfferTemplateResponseModel> = {}
): CollectiveOfferTemplateResponseModel => {
  const currentId = offerTemplateId++

  return {
    id: currentId,
    displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
    name: `Offre vitrine ${currentId}`,
    venue: listOffersVenueFactory(),
    dates: {
      start: new Date().toISOString(),
      end: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
    },
    allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE],
    location: {
      locationType: CollectiveLocationType.SCHOOL,
      location: null,
      locationComment: null,
    },
    ...customCollectiveOfferTemplate,
  }
}

export const listOffersVenueFactory = (
  customListOffersVenue: Partial<ListOffersVenueResponseModel> = {}
): ListOffersVenueResponseModel => ({
  id: 1,
  name: 'Nom de la structure',
  publicName: 'Nom public de la structure',
  offererName: 'offerer name',
  isVirtual: false,
  ...customListOffersVenue,
})

const sharedCollectiveOfferData = {
  isActive: true,
  displayedStatus: CollectiveOfferDisplayedStatus.PUBLISHED,
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
  isPublicApi: false,
  id: 123,
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
  location: {
    locationType: CollectiveLocationType.SCHOOL,
    address: null,
    locationComment: null,
  },
}

export const getCollectiveOfferFactory = (
  customCollectiveOffer: Partial<GetCollectiveOfferResponseModel> = {}
): GetCollectiveOfferResponseModel => {
  const currentOfferId = offerId++
  return {
    ...sharedCollectiveOfferData,
    id: currentOfferId,
    venue: getCollectiveOfferVenueFactory(),
    isTemplate: false,
    allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
    collectiveStock: getCollectiveOfferCollectiveStockFactory(),
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
    name: `Nom de la structure ${currentVenueId}`,
    managingOfferer: getCollectiveOfferManagingOffererFactory(),
    publicName: `Nom public de la structure ${currentVenueId}`,
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
    name: `Nom de l'entité ${currentOffererId}`,
    siren: '123456789',
    ...customGetCollectiveOfferManagingOfferer,
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
  hasAdageId: true,
  hasOffers: true,
  hasActiveIndividualOffer: true,
  hasPartnerPage: false,
  isOpenToPublic: true,
  isVirtual: false,
  managingOfferer: {
    id: 1,
    isValidated: true,
    name: 'Ma super structure',
    siren: '',
  },
  mentalDisabilityCompliant: true,
  motorDisabilityCompliant: false,
  name: 'Nom de la structure',
  publicName: 'Nom public de la structure',
  venueType: { value: VenueTypeCode.CENTRE_CULTUREL, label: 'Centre culturel' },
  visualDisabilityCompliant: true,
  openingHours: null,
  isCaledonian: false,
  isActive: true,
  isValidated: true,
  allowedOnAdage: true,
  hasNonFreeOffers: true,
  canDisplayHighlights: true,
}

export const defaultGetCollectiveOfferRequest: GetCollectiveOfferRequestResponseModel =
  {
    dateCreated: new Date().toISOString(),
    phoneNumber: null,
    requestedDate: null,
    totalStudents: null,
    totalTeachers: null,
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
