import { OfferAddressType, OfferStatus } from 'apiClient/v1'

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
