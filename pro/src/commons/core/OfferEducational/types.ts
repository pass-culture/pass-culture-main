import type {
  CollectiveLocationType,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
  EacFormat,
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  StudentLevels,
} from '@/apiClient/v1'
import type {
  AccessibilityFormValues,
  AddressFormValues,
} from '@/commons/core/shared/types'
import { hasProperty } from '@/commons/utils/types'

export type OfferDatesType = 'permanent' | 'specific_dates'

export type CollectiveOffer =
  | CollectiveOfferTemplateResponseModel
  | CollectiveOfferResponseModel

export interface OfferEducationalFormValues extends Partial<AddressFormValues> {
  title: string
  description: string
  duration?: string
  offererId: string
  venueId: string
  location?: {
    locationType?: CollectiveLocationType
    location?: {
      id?: string
      isManualEdition?: boolean
      isVenueLocation?: boolean
      label?: string
    }
    locationComment?: string | null
  }
  interventionArea?: string[]
  participants: {
    [K in StudentLevels]?: boolean
  }
  accessibility: AccessibilityFormValues
  phone?: string
  email?: string
  contactFormType?: 'form' | 'url'
  contactUrl?: string | null
  contactOptions?: { phone: boolean; email: boolean; form: boolean }
  notificationEmails?: { email: string }[]
  domains?: string[]
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
  formats: EacFormat[]
}

export enum Mode {
  CREATION,
  EDITION,
  READ_ONLY,
}

export type OfferEducationalStockFormValues = {
  startDatetime: string
  endDatetime: string
  eventTime: string
  numberOfPlaces: number | null
  totalPrice: number | null
  bookingLimitDatetime: string
  priceDetail: string
}

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

export enum CollectiveOffersSortingColumn {
  EVENT_DATE = 'EVENT_DATE',
}

export const isCollectiveOfferBookable = (
  offer:
    | CollectiveOfferResponseModel
    | CollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
    | GetCollectiveOfferTemplateResponseModel
): offer is CollectiveOfferResponseModel => {
  return 'stock' in offer
}
