import {
  EducationalInstitutionResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  SubcategoryIdEnum,
} from 'apiClient/v1'

import { GetOfferVenueResponseModel } from 'apiClient/v1'

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
  subCategory: SubcategoryIdEnum
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
  domains: string[]
  'search-domains'?: string
}

export type CanOffererCreateCollectiveOffer = Adapter<
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
  institution?: EducationalInstitutionResponseModel | null
}

export enum EducationalOfferType {
  SHOWCASE = 'SHOWCASE',
  CLASSIC = 'CLASSIC',
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
  domains: EducationalDomain[]
  institution?: EducationalInstitutionResponseModel | null
  isEditable: boolean
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

export type EducationalDomain = {
  id: number
  name: string
}

export type VisibilityFormValues = {
  visibility: 'all' | 'one'
  institution: string
  'search-institution': string
}
