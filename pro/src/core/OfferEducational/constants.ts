import {
  IOfferEducationalFormValues,
  ADRESS_TYPE,
  OfferEducationalStockFormValues,
  EducationalOfferType,
} from './types'

export const DEFAULT_EAC_FORM_VALUES: IOfferEducationalFormValues = {
  category: '',
  subCategory: '',
  title: '',
  description: '',
  duration: '',
  offererId: '',
  venueId: '',
  eventAddress: {
    addressType: ADRESS_TYPE.OFFERER_VENUE,
    otherAddress: '',
    venueId: '',
  },
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
}

export const PARTICIPANTS: Record<string, string> = {
  quatrieme: 'Collège - 4e',
  troisieme: 'Collège - 3e',
  CAPAnnee1: 'CAP - 1re année',
  CAPAnnee2: 'CAP - 2e année',
  seconde: 'Lycée - Seconde',
  premiere: 'Lycée - Première',
  terminale: 'Lycée - Terminale',
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
