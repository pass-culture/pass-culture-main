import { OfferAddressType } from 'api/v1/gen'

export enum OfferStatus {
  OFFER_STATUS_ACTIVE = 'ACTIVE',
  OFFER_STATUS_INACTIVE = 'INACTIVE',
  OFFER_STATUS_SOLD_OUT = 'SOLD_OUT',
  OFFER_STATUS_EXPIRED = 'EXPIRED',
  OFFER_STATUS_PENDING = 'PENDING',
  OFFER_STATUS_REJECTED = 'REJECTED',
  OFFER_STATUS_DRAFT = 'DRAFT',
}

type Venue = {
  departementCode: string
  managingOffererId: string
}

type Stock = {
  bookingsQuantity: number
}

export type Offer = {
  id: string
  bookingEmail?: string
  description?: string
  durationMinutes?: number
  extraData?: {
    students?: string[]
    contactEmail?: string
    contactPhone?: string
    offerVenue?: {
      venueId: string
      otherAddress: string
      addressType: OfferAddressType
    }
    isShowcase?: boolean
  }
  stocks: Stock[]
  isActive: boolean
  isEducational: boolean
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  name: string
  subcategoryId: string
  venueId: string
  status: OfferStatus
  venue: Venue
  isBooked: boolean
}
