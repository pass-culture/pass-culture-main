import { EacFormat } from 'apiClient/adage'
import {
  EducationalInstitutionResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { AccessibiltyFormValues } from 'core/shared'
import { hasProperty } from 'utils/types'

export type OfferDatesType = 'permanent' | 'specific_dates'

export type OfferEducationalFormValues = {
  title: string
  description: string
  duration: string
  offererId: string
  venueId: string
  eventAddress: {
    addressType: OfferAddressType
    otherAddress: string
    venueId: number | null
  }
  interventionArea: string[]
  participants: Record<StudentLevels | 'all', boolean>
  accessibility: AccessibiltyFormValues
  phone: string
  email: string
  notificationEmails: string[]
  domains: string[]
  'search-domains'?: string
  'search-interventionArea'?: string
  'search-formats'?: string
  priceDetail?: string
  imageUrl?: string
  imageCredit?: string
  nationalProgramId?: string
  isTemplate: boolean
  datesType?: OfferDatesType
  beginningDate?: string
  endingDate?: string
  hour?: string
  formats?: EacFormat[]
}

export enum Mode {
  CREATION,
  EDITION,
  READ_ONLY,
}

export type OfferEducationalStockFormValues = {
  eventDate: string
  eventTime: string
  numberOfPlaces: number | ''
  totalPrice: number | ''
  bookingLimitDatetime: string
  priceDetail: string
  educationalOfferType: EducationalOfferType
}

export type GetStockOfferSuccessPayload = {
  isActive: boolean
  status: OfferStatus
  isBooked: boolean
  isCancellable: boolean
  venueDepartmentCode: string
  managingOffererId: number
  isEducational: boolean
  isShowcase: boolean
  offerId?: number | null
  institution?: EducationalInstitutionResponseModel | null
  name: string
}

export enum EducationalOfferType {
  SHOWCASE = 'SHOWCASE',
  CLASSIC = 'CLASSIC',
}

export const isOfferEducational = (
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
): offer is CollectiveOfferResponseModel => offer.isEducational

export const isCollectiveOffer = (
  value: unknown
): value is GetCollectiveOfferResponseModel =>
  // Could be enhanced to check that it is also a GetCollectiveOfferTemplateResponseModel
  hasProperty(value, 'isTemplate') && value.isTemplate === false

export const isCollectiveOfferTemplate = (
  value: unknown
): value is GetCollectiveOfferTemplateResponseModel =>
  // Could be enhanced to check that it is also a GetCollectiveOfferTemplateResponseModel
  hasProperty(value, 'isTemplate') && value.isTemplate === true

export type VisibilityFormValues = {
  visibility: 'all' | 'one'
  institution: string
  'search-institution': string
  'search-teacher': string | null
  teacher: string | null
}

export enum CollectiveOfferStatus {
  ACTIVE = 'ACTIVE',
  PENDING = 'PENDING',
  REJECTED = 'REJECTED',
  PREBOOKED = 'PREBOOKED',
  BOOKED = 'BOOKED',
  INACTIVE = 'INACTIVE',
  EXPIRED = 'EXPIRED',
  ENDED = 'ENDED',
}
