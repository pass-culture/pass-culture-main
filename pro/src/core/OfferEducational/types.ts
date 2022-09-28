import {
  EducationalInstitutionResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  SubcategoryIdEnum,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
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

export type CollectiveOffer = GetCollectiveOfferResponseModel & {
  isTemplate: false
}

export type CollectiveOfferTemplate =
  GetCollectiveOfferTemplateResponseModel & {
    isTemplate: true
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
