import {
  GetOfferVenueResponseModel,
  OfferAddressType,
  OfferStatus,
  StudentLevels,
} from 'api/v1/gen'

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

export type CollectiveOfferResponseModel = {
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
  offerId?: string | null
  contactEmail: string
  contactPhone: string
  hasBookingLimitDatetimesPassed: boolean
  id: string
  isActive: boolean
  isBookable: boolean
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  nonHumanizedId: number
  visualDisabilityCompliant: boolean
  name: string
  collectiveStock: {
    id: string
    isBooked: boolean
  }
  subcategoryId: string
  venue: GetOfferVenueResponseModel
  venueId: string
  status: OfferStatus
}

export type CollectiveOffer = CollectiveOfferResponseModel & {
  isBooked: boolean
}
