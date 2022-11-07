import {
  EducationalInstitutionResponseModel,
  WithdrawalTypeEnum,
  OfferStatus,
} from 'apiClient/v1'
import { ICropParams } from 'components/ImageUploader'
import { IAccessibiltyFormValues } from 'core/shared'

import { CATEGORY_STATUS } from '.'

export type TSearchFilters = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  status: OfferStatus | 'all'
  creationMode: string
  collectiveOfferType: string
  periodBeginningDate: string
  periodEndingDate: string
}

export type Offerer = {
  id: string
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
}

export type Offer = {
  id: string
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
  isEditable: boolean
  isShowcase?: boolean | null
  educationalInstitution?: EducationalInstitutionResponseModel | null
}

export type Option = {
  id: string
  displayName: string
}

export interface ICategorySubtypeItem {
  code: number
  label: string
  children: {
    code: number
    label: string
  }[]
}

export interface IOfferCategory {
  id: string
  proLabel: string
  isSelectable: boolean
}

export interface IOfferSubCategory {
  id: string
  categoryId: string
  proLabel: string
  isEvent: boolean
  conditionalFields: string[]
  canBeDuo: boolean
  canBeEducational: boolean
  onlineOfflinePlatform: CATEGORY_STATUS
  reimbursementRule: string
  isSelectable: boolean
}

export interface IOfferIndividualStock {
  beginningDatetime: string | null
  bookingLimitDatetime: string | null
  bookingsQuantity: number
  dateCreated: Date
  hasActivationCode: boolean
  id: string
  isEventDeletable: boolean
  isEventExpired: boolean
  isSoftDeleted: boolean
  offerId: string
  price: number
  quantity?: number | null
  remainingQuantity: number | null
}

export interface IOfferIndividualOfferer {
  id: string
  name: string
}

export interface IOfferIndividualVenue {
  id: string
  name: string
  publicName: string
  isVirtual: boolean
  address: string
  postalCode: string
  city: string
  offerer: IOfferIndividualOfferer
  departmentCode: string
  accessibility: IAccessibiltyFormValues
}

// TODO: this should be generated in openapi schema
export interface IOfferExtraData {
  author?: string
  isbn?: string
  musicType?: string
  musicSubType?: string
  performer?: string
  showType?: string
  showSubType?: string
  speaker?: string
  stageDirector?: string
  visa?: string
}

export interface IOfferIndividualVenueProvider {
  id: string
  isActive: boolean
  name: string
}

export interface IOfferIndividualImage {
  originalUrl: string
  url: string
  credit: string
  cropParams?: ICropParams
}

export interface IOfferIndividual {
  id: string
  nonHumanizedId: number
  author: string
  bookingEmail: string
  description: string
  durationMinutes: number | null
  isbn: string
  isActive: boolean
  isDuo: boolean
  isEducational: boolean
  isEvent: boolean
  isDigital: boolean
  accessibility: IAccessibiltyFormValues
  isNational: boolean
  name: string
  musicSubType: string
  musicType: string
  offererId: string
  offererName: string
  performer: string
  showSubType: string
  showType: string
  stageDirector: string
  speaker: string
  subcategoryId: string
  image?: IOfferIndividualImage
  url: string
  externalTicketOfficeUrl: string
  venueId: string
  venue: IOfferIndividualVenue
  visa: string
  withdrawalDetails: string | null
  withdrawalDelay?: number | null
  withdrawalType: WithdrawalTypeEnum | null
  stocks: IOfferIndividualStock[]
  lastProviderName: string | null
  lastProvider: IOfferIndividualVenueProvider | null
  status: OfferStatus
}
