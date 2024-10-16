import { OfferAddressType } from 'apiClient/v1'

import {
  EducationalOfferType,
  OfferEducationalFormValues,
  OfferEducationalStockFormValues,
  VisibilityFormValues,
} from './types'
import { buildStudentLevelsMapWithDefaultValue } from './utils/buildStudentLevelsMapWithDefaultValue'

export const DEFAULT_EAC_FORM_VALUES: OfferEducationalFormValues = {
  title: '',
  description: '',
  duration: '',
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: OfferAddressType.OFFERER_VENUE,
    otherAddress: '',
    venueId: 0,
  },
  interventionArea: [],
  participants: {
    all: false,
    ...buildStudentLevelsMapWithDefaultValue(false),
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
  notificationEmails: [''],
  domains: [],
  'search-domains': '',
  'search-formats': '',
  'search-interventionArea': '',
  priceDetail: '',
  imageUrl: '',
  imageCredit: '',
  nationalProgramId: '',
  isTemplate: false,
  datesType: 'permanent',
  beginningDate: '',
  endingDate: '',
  hour: '',
  formats: [],
  contactOptions: {
    phone: false,
    email: false,
    form: false,
  },
  contactFormType: 'form',
}

export const DEFAULT_EAC_STOCK_FORM_VALUES: OfferEducationalStockFormValues = {
  startDatetime: '',
  endDatetime: '',
  eventTime: '',
  numberOfPlaces: '',
  totalPrice: '',
  bookingLimitDatetime: '',
  priceDetail: '',
  educationalOfferType: EducationalOfferType.CLASSIC,
}

export const DEFAULT_VISIBILITY_FORM_VALUES: VisibilityFormValues = {
  visibility: 'one',
  institution: '',
  'search-institution': '',
  'search-teacher': '',
  teacher: null,
}

export const MAX_DETAILS_LENGTH = 1000

export const offerAdageActivated =
  'Votre offre est maintenant active et visible dans ADAGE'
export const offerAdageDeactivate =
  'Votre offre est désactivée et n’est plus visible sur ADAGE'
