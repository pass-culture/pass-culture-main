import { GetOfferResponseModel } from 'api/v1/gen/'

export type TSearchFilters = {
  nameOrIsbn: string
  offererId: string
  venueId: string
  categoryId: string
  status: string
  creationMode: string
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
  status: string
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
}

export type Option = {
  id: string
  displayName: string
}

export interface IApiOfferIndividual extends GetOfferResponseModel {
  withdrawalDelay: number | null
  extraData?: {
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
}

export interface IOfferIndividual {
  author: string
  bookingEmail: string
  description: string
  durationMinutes: number | null
  isbn: string
  isDuo: boolean
  isEducational: boolean
  noDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  isNational: boolean
  name: string
  musicSubType: string
  musicType: string
  offererId: string
  performer: string
  showSubType: string
  showType: string
  stageDirector: string
  speaker: string
  subcategoryId: string
  url: string
  externalTicketOfficeUrl: string
  venueId: string
  visa: string
  withdrawalDetails: string | null
  withdrawalDelay?: number | null
}
