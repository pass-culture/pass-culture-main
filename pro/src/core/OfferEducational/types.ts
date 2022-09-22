import {
  EducationalInstitutionResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  SubcategoryIdEnum,
  GetOfferVenueResponseModel,
} from 'apiClient/v1'
import { IAccessibiltyFormValues } from 'core/shared'

export type IEducationalCategory = {
  id: string
  label: string
}

export type IEducationalSubCategory = {
  id: string
  categoryId: string
  label: string
}

export type EducationalCategories = {
  educationalCategories: IEducationalCategory[]
  educationalSubCategories: IEducationalSubCategory[]
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
  interventionArea: string[]
  participants: Record<StudentLevels | 'all', boolean>
  accessibility: IAccessibiltyFormValues
  phone: string
  email: string
  notifications: boolean
  notificationEmails: string[]
  domains: string[]
  'search-domains'?: string
  'search-interventionArea'?: string
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
  isCancellable: boolean
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
