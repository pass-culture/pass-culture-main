import {
  CollectiveOffersBookingResponseModel,
  EacFormat,
  EducationalInstitutionResponseModel,
  GetOfferLastProviderResponseModel,
  GetOfferVenueResponseModel,
  OfferStatus,
  PriceCategoryResponseModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { CropParams } from 'components/ImageUploader'
import { CollectiveOfferStatus } from 'core/OfferEducational'
import { AccessibiltyFormValues } from 'core/shared'

import { ALL_FORMATS, ALL_STATUS } from './constants'

export type SearchFiltersParams = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  format: EacFormat | typeof ALL_FORMATS
  status: OfferStatus | CollectiveOfferStatus | typeof ALL_STATUS
  creationMode: string
  collectiveOfferType: string
  periodBeginningDate: string
  periodEndingDate: string
  page?: number
}

export type Offerer = {
  id: number
  name: string
}

export type Venue = {
  name: string
  publicName?: string | null
  offererName: string
  isVirtual: boolean
  departementCode?: string | null
}

export type Stock = {
  beginningDatetime?: Date | null
  remainingQuantity: string | number
  bookingLimitDatetime?: Date | null
  bookingQuantity?: number | null
}

export type Offer = {
  id: number
  status: OfferStatus
  isActive: boolean
  hasBookingLimitDatetimesPassed: boolean
  thumbUrl?: string | null
  isEducational: boolean
  name: string
  isEvent: boolean
  productIsbn?: string | null
  venue: Venue
  stocks: Stock[]
  isPublicApi?: boolean | null
  isEditable: boolean
  isShowcase?: boolean | null
  educationalInstitution?: EducationalInstitutionResponseModel | null
  educationalBooking?: CollectiveOffersBookingResponseModel | null
}

export interface CategorySubtypeItem {
  code: number
  label: string
  children: {
    code: number
    label: string
  }[]
}

// TODO: this should be generated in openapi schema
export interface OfferExtraData {
  author?: string
  gtl_id?: string
  performer?: string
  ean?: string
  showType?: string
  showSubType?: string
  speaker?: string
  stageDirector?: string
  visa?: string
}

export interface OfferCollectiveImage {
  url?: string | null
  credit?: string | null
}

export interface IndividualOfferImage {
  originalUrl: string
  url: string
  credit: string | null
  cropParams?: CropParams
}

export interface IndividualOffer {
  id: number
  author: string
  bookingEmail: string
  bookingsCount: number
  description: string
  durationMinutes: number | null
  hasStocks: boolean
  isActive: boolean
  isActivable: boolean
  isDuo: boolean
  isEvent: boolean
  isDigital: boolean
  accessibility: AccessibiltyFormValues
  isNational: boolean
  name: string
  gtl_id?: string
  performer: string
  priceCategories?: PriceCategoryResponseModel[] | null
  ean: string
  showSubType: string
  showType: string
  stageDirector: string
  speaker: string
  subcategoryId: string
  image?: IndividualOfferImage
  url: string
  externalTicketOfficeUrl: string
  venue: GetOfferVenueResponseModel
  visa: string
  withdrawalDetails: string | null
  withdrawalDelay?: number | null
  withdrawalType: WithdrawalTypeEnum | null
  lastProviderName: string | null
  lastProvider?: GetOfferLastProviderResponseModel | null
  status: OfferStatus
  bookingContact?: string | null
}
