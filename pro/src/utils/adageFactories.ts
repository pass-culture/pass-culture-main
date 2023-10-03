import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CategoriesResponseModel,
  CollectiveOfferTemplateResponseModel,
  EducationalInstitutionWithBudgetResponseModel,
  OfferAddressType,
} from 'apiClient/adage'

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
    name: 'Mon offre vitrine',
    offerVenue: {
      venueId: 1,
      otherAddress: '',
      addressType: OfferAddressType.OFFERER_VENUE,
    },
    students: [],
    subcategoryLabel: 'Cinéma',
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
  }

export const defaultAdageUser: AuthenticatedResponse = {
  departmentCode: '75',
  email: 'test@example.com',
  institutionCity: 'Paris',
  institutionName: 'Mon établissement',
  role: AdageFrontRoles.REDACTOR,
  uai: '1234567A',
  lat: null,
  lon: null,
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
  objectID: '481',
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
  isTemplate: false,
  __queryID: 'queryId',
  __position: 0,
}
export const defaultUseInfiniteHitsReturn = {
  hits: [hit],
  isLastPage: true,
  showMore: vi.fn(),
  showPrevious: vi.fn(),
  isFirstPage: true,
  sendEvent: vi.fn(),
  bindEvent: vi.fn(),
  currentPageHits: [hit],
}

export const defaultCategories: CategoriesResponseModel = {
  categories: [{ id: 'CINEMA', proLabel: 'Cinéma' }],
  subcategories: [
    {
      id: 'CINE_PLEIN_AIR',
      categoryId: 'CINEMA',
    },
    {
      id: 'EVENEMENT_CINE',
      categoryId: 'CINEMA',
    },
  ],
}
