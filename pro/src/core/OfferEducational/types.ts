import {
  GetOfferVenueResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
} from 'api/v1/gen'

export type IUserVenue = {
  id: string
  name: string
  address: {
    street: string
    city: string
    postalCode: string
  }
}

export type IUserOfferer = {
  id: string
  name: string
  managedVenues: IUserVenue[]
}

export enum ACCESSIBILITY {
  VISUAL = 'visual',
  MENTAL = 'mental',
  AUDIO = 'audio',
  MOTOR = 'motor',
  NONE = 'none',
}

export type IEducationalCategory = {
  id: string
  label: string
}

export type IEducationalSubCategory = {
  id: string
  categoryId: string
  label: string
}

export type IOfferEducationalFormValues = {
  category: string
  subCategory: string
  title: string
  description: string
  duration: string
  offererId: string
  venueId: string
  eventAddress: {
    addressType: OfferAddressType
    otherAddress: string
    venueId: string
  }
  participants: {
    quatrieme: boolean
    troisieme: boolean
    CAPAnnee1: boolean
    CAPAnnee2: boolean
    seconde: boolean
    premiere: boolean
    terminale: boolean
  }
  accessibility: {
    visual: boolean
    audio: boolean
    motor: boolean
    mental: boolean
    none: boolean
  }
  phone: string
  email: string
  notifications: boolean
  notificationEmail: string
}

export type GetIsOffererEligible = Adapter<
  string,
  { isOffererEligibleToEducationalOffer: boolean },
  { isOffererEligibleToEducationalOffer: false }
>

export enum Mode {
  CREATION,
  EDITION,
  READ_ONLY,
}

export type EducationalOfferModelPayload = {
  offererId: string
  venueId: string
  subcategoryId: string
  name: string
  bookingEmail?: string
  description?: string
  durationMinutes?: number
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  extraData: {
    students: string[]
    contactEmail: string
    contactPhone: string
    offerVenue: {
      addressType: OfferAddressType
      otherAddress: string
      venueId: string
    }
  }
}

export type OfferEducationalStockFormValues = {
  eventDate: Date | ''
  eventTime: Date | ''
  numberOfPlaces: number | ''
  totalPrice: number | ''
  bookingLimitDatetime: Date | null
  priceDetail: string
  educationalOfferType: EducationalOfferType
}

export type StockPayload = {
  beginningDatetime: Date
  bookingLimitDatetime: Date | null
  totalPrice: number
  numberOfTickets: number
  educationalPriceDetail: string
}

export type CreateCollectiveStockPayload = {
  offerId: string
  beginningDatetime: Date
  bookingLimitDatetime: Date | null
  totalPrice: number
  numberOfTickets: number
  educationalPriceDetail: string
}

export type CreateCollectiveOfferTemplatePayload = {
  educationalPriceDetail: string
}

export type GetStockOfferSuccessPayload = {
  id: string
  isActive: boolean
  status: OfferStatus
  isBooked: boolean
  venueDepartmentCode: string
  managingOffererId: string
  isEducational: boolean
  isShowcase: boolean
  offerId?: string | null
}

export enum EducationalOfferType {
  SHOWCASE = 'SHOWCASE',
  CLASSIC = 'CLASSIC',
}

export type CollectiveStockResponseModel = {
  id: string
  beginningDatetime?: string
  bookingLimitDatetime?: string
  price: number
  numberOfTickets?: number
  isEducationalStockEditable?: boolean
  educationalPriceDetail?: string
  stockId?: string
}

type CollectiveOfferBaseResponseModel = {
  id: string
  bookingEmail?: string | null
  dateCreated: Date
  description?: string | null
  durationMinutes?: number | null
  students: StudentLevels[]
  offerVenue: {
    addressType: OfferAddressType
    otherAddress: string
    venueId: string
  }
  contactEmail: string
  contactPhone: string
  hasBookingLimitDatetimesPassed: boolean
  isActive: boolean
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  nonHumanizedId: number
  name: string
  subcategoryId: string
  venue: GetOfferVenueResponseModel
  venueId: string
  status: OfferStatus
  offerId?: string | null
}

export type CollectiveOfferResponseModel = CollectiveOfferBaseResponseModel & {
  isBookable: boolean
  collectiveStock: {
    id: string
    isBooked: boolean
  }
}

export type CollectiveOffer = CollectiveOfferResponseModel & {
  isBooked: boolean
}

export type CollectiveOfferTemplateResponseModel =
  CollectiveOfferBaseResponseModel & {
    educationalPriceDetail: string
  }

export type CollectiveOfferTemplate = CollectiveOfferTemplateResponseModel & {
  isBooked: boolean
}

export type StockResponse = {
  id: string
  beginningDatetime?: string
  bookingLimitDatetime?: string
  price: number
  numberOfTickets?: number
  isEducationalStockEditable?: boolean
  educationalPriceDetail?: string
}
