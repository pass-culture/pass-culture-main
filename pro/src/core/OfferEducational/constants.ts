import { OfferAddressType, StudentLevels } from 'api/v1/gen'

import {
  IOfferEducationalFormValues,
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
    addressType: OfferAddressType.OffererVenue,
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

export const PARTICIPANTS: Record<string, StudentLevels> = {
  quatrieme: StudentLevels.Collge4e,
  troisieme: StudentLevels.Collge3e,
  CAPAnnee1: StudentLevels.CAP1reAnne,
  CAPAnnee2: StudentLevels.CAP2eAnne,
  seconde: StudentLevels.LyceSeconde,
  premiere: StudentLevels.LycePremire,
  terminale: StudentLevels.LyceTerminale,
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
