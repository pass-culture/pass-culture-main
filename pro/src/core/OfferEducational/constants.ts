import {
  OfferAddressType,
  StudentLevels,
  SubcategoryIdEnum,
} from 'apiClient/v1'

import {
  EducationalOfferType,
  IOfferEducationalFormValues,
  OfferEducationalStockFormValues,
  VisibilityFormValues,
} from './types'

export const DEFAULT_EAC_FORM_VALUES: IOfferEducationalFormValues = {
  category: '',
  subCategory: '' as SubcategoryIdEnum,
  title: '',
  description: '',
  duration: '',
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: '',
  },
  interventionArea: [],
  participants: {
    quatrieme: false,
    troisieme: false,
    CAPAnnee1: false,
    CAPAnnee2: false,
    seconde: false,
    premiere: false,
    terminale: false,
  },
  accessibility: {
    visual: false,
    audio: false,
    motor: false,
    mental: false,
    none: false,
  },
  phone: '',
  email: '',
  notifications: false,
  notificationEmail: '',
  domains: [],
  'search-domains': '',
  'search-interventionArea': '',
}

export const PARTICIPANTS: Record<string, StudentLevels> = {
  quatrieme: StudentLevels.COLL_GE_4E,
  troisieme: StudentLevels.COLL_GE_3E,
  CAPAnnee1: StudentLevels.CAP_1RE_ANN_E,
  CAPAnnee2: StudentLevels.CAP_2E_ANN_E,
  seconde: StudentLevels.LYC_E_SECONDE,
  premiere: StudentLevels.LYC_E_PREMI_RE,
  terminale: StudentLevels.LYC_E_TERMINALE,
}

export const DEFAULT_EAC_STOCK_FORM_VALUES: OfferEducationalStockFormValues = {
  eventDate: '',
  eventTime: '',
  numberOfPlaces: '',
  totalPrice: '',
  bookingLimitDatetime: null,
  priceDetail: '',
  educationalOfferType: EducationalOfferType.CLASSIC,
}

export const DEFAULT_VISIBILITY_FORM_VALUES: VisibilityFormValues = {
  visibility: 'all',
  institution: '',
  'search-institution': '',
}
