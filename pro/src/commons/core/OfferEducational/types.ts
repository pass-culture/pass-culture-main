import { EacFormat } from 'apiClient/adage'
import {
  CollectiveOfferResponseModel,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  ListOffersOfferResponseModel,
  OfferAddressType,
  StudentLevels,
} from 'apiClient/v1'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import { type EnumType } from 'commons/custom_types/utils'
import { hasProperty } from 'commons/utils/types'

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
  accessibility: AccessibilityFormValues
  phone: string
  email: string
  contactFormType?: 'form' | 'url'
  contactUrl?: string | null
  contactOptions?: { phone: boolean; email: boolean; form: boolean }
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

export const Mode = {
  CREATION: 0,
  EDITION: 1,
  READ_ONLY: 2,
} as const
// eslint-disable-next-line no-redeclare
export type Mode = EnumType<typeof Mode>

export type OfferEducationalStockFormValues = {
  startDatetime: string
  endDatetime: string
  eventTime: string
  numberOfPlaces: number | ''
  totalPrice: number | ''
  bookingLimitDatetime: string
  priceDetail: string
  educationalOfferType: EducationalOfferType
}

export const EducationalOfferType = {
  SHOWCASE: 'SHOWCASE',
  CLASSIC: 'CLASSIC',
} as const
// eslint-disable-next-line no-redeclare
export type EducationalOfferType = EnumType<typeof EducationalOfferType>

export const isOfferEducational = (
  offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
): offer is CollectiveOfferResponseModel => offer.isEducational

export const isCollectiveOffer = (
  value: unknown
): value is GetCollectiveOfferResponseModel =>
  // Could be enhanced to check that it is also a GetCollectiveOfferTemplateResponseModel
  (hasProperty(value, 'isTemplate') && value.isTemplate === false) ||
  (hasProperty(value, 'isShowcase') && value.isShowcase === false)

export const isCollectiveOfferTemplate = (
  value: unknown
): value is GetCollectiveOfferTemplateResponseModel =>
  // Could be enhanced to check that it is also a GetCollectiveOfferTemplateResponseModel
  (hasProperty(value, 'isTemplate') && value.isTemplate === true) ||
  (hasProperty(value, 'isShowcase') && value.isShowcase === true)

export type VisibilityFormValues = {
  visibility: 'all' | 'one'
  institution: string
  'search-institution': string
  'search-teacher': string | null
  teacher: string | null
}

export const CollectiveOffersSortingColumn = {
  EVENT_DATE: 'EVENT_DATE',
} as const
// eslint-disable-next-line no-redeclare
export type CollectiveOffersSortingColumn = EnumType<
  typeof CollectiveOffersSortingColumn
>
