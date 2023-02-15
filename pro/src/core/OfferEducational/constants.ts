import { OfferAddressType, SubcategoryIdEnum } from 'apiClient/v1'

import {
  EducationalOfferType,
  IOfferEducationalFormValues,
  OfferEducationalStockFormValues,
  VisibilityFormValues,
} from './types'
import { buildStudentLevelsMapWithDefaultValue } from './utils/buildStudentLevelsMapWithDefaultValue'

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
  'search-interventionArea': '',
  priceDetail: '',
  imageUrl: '',
  imageCredit: '',
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
  visibility: 'one',
  institution: '',
  'search-institution': '',
}

export const MAX_DETAILS_LENGTH = 1000

export const offerAdageActivated =
  'Votre offre est maintenant active et visible dans ADAGE'
export const offerAdageDeactivate =
  'Votre offre est désactivée et n’est plus visible sur ADAGE'
