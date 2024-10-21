import { addDays } from 'date-fns'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  EacFormat,
  EducationalInstitutionWithBudgetResponseModel,
  OfferAddressType,
} from 'apiClient/adage'
import { StudentLevels } from 'apiClient/v1'

export const defaultCollectiveTemplateOffer: CollectiveOfferTemplateResponseModel =
  {
    audioDisabilityCompliant: false,
    visualDisabilityCompliant: false,
    mentalDisabilityCompliant: true,
    motorDisabilityCompliant: true,
    contactEmail: 'test@example.com',
    domains: [],
    id: 1,
    interventionArea: [],
    isExpired: false,
    isSoldOut: false,
    isFavorite: false,
    isTemplate: true,
    name: 'Mon offre vitrine',
    offerVenue: {
      venueId: 1,
      otherAddress: '',
      addressType: OfferAddressType.OFFERER_VENUE,
    },
    students: [],
    venue: {
      id: 1,
      address: '1 boulevard Poissonnière',
      city: 'Paris',
      name: 'Mon lieu',
      postalCode: '75000',
      publicName: 'Mon lieu nom publique',
      managingOfferer: {
        name: 'Ma super structure',
      },
      coordinates: {
        latitude: 48.87004,
        longitude: 2.3785,
      },
    },
    dates: {
      start: new Date().toISOString(),
      end: addDays(new Date(), 1).toISOString(),
    },
  }

export const defaultCollectiveOffer: CollectiveOfferResponseModel = {
  id: 479,
  name: 'Une chouette à la mer',
  description: 'Une offre vraiment chouette',
  stock: {
    id: 825,
    startDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
    bookingLimitDatetime: new Date('2022-09-16T00:00:00Z').toISOString(),
    isBookable: true,
    price: 140000,
    numberOfTickets: 10,
  },
  venue: {
    id: 1,
    address: '1 boulevard Poissonnière',
    city: 'Paris',
    name: 'Le Petit Rintintin 33',
    postalCode: '75000',
    publicName: 'Le Petit Rintintin 33',
    coordinates: {
      latitude: 48.87004,
      longitude: 2.3785,
    },
    managingOfferer: {
      name: 'Le Petit Rintintin Management',
    },
  },
  isSoldOut: false,
  isExpired: false,
  isFavorite: false,
  visualDisabilityCompliant: true,
  mentalDisabilityCompliant: true,
  audioDisabilityCompliant: true,
  motorDisabilityCompliant: true,
  contactEmail: '',
  contactPhone: '',
  domains: [],
  offerVenue: {
    venueId: 1,
    otherAddress: '',
    addressType: OfferAddressType.OFFERER_VENUE,
  },
  teacher: {
    firstName: 'Jean',
    lastName: 'Dupont',
  },
  students: [StudentLevels.COLL_GE_4E, StudentLevels.COLL_GE_3E],
  interventionArea: ['75', '92'],
  formats: [EacFormat.CONCERT],
}

export const defaultAdageUser: AuthenticatedResponse = {
  departmentCode: '75',
  email: 'test@example.com',
  institutionCity: 'Paris',
  institutionName: 'Mon établissement',
  role: AdageFrontRoles.REDACTOR,
  uai: '1234567A',
  lat: 1,
  lon: 2,
}

export const defaultEducationalInstitution: EducationalInstitutionWithBudgetResponseModel =
  {
    budget: 1000,
    city: 'Paris',
    id: 1,
    institutionType: 'COLLEGE',
    name: 'Mon établissement',
    phoneNumber: '0123456789',
    postalCode: '75000',
  }

export const defaultUseStatsReturn = {
  nbHits: 0,
  nbPages: 0,
  areHitsSorted: false,
  page: 0,
  processingTimeMS: 0,
  query: '',
}

const hit = {
  objectID: 'T-481',
  offer: {
    dates: [new Date('2021-09-29T13:54:30+00:00').valueOf()],
    name: 'titre',
    thumbUrl: '',
  },
  venue: {
    name: 'lieu',
    publicName: 'lieu public',
  },
  _highlightResult: {},
  isTemplate: true,
  __queryID: 'queryId',
  __position: 0,
}
export const defaultUseInfiniteHitsReturn = {
  items: [hit],
  hits: [hit],
  isLastPage: true,
  showMore: vi.fn(),
  showPrevious: vi.fn(),
  isFirstPage: true,
  sendEvent: vi.fn(),
  bindEvent: vi.fn(),
  currentPageHits: [hit],
}
