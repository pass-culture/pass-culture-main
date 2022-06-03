import {
  OfferAddressType,
  OfferStockResponse,
  OfferVenueResponse,
} from 'api/gen'

export type EducationalDomain = {
  id: number
  name: string
}

export interface OfferType {
  id: number
  name: string
  subcategoryLabel: string
  description?: string | null
  venue: OfferVenueResponse
  stocks: OfferStockResponse[]
  isSoldOut: boolean
  isExpired: boolean
  durationMinutes?: number | null
  mentalDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  extraData?: {
    contactEmail?: string
    contactPhone?: string
    offerVenue: {
      addressType: OfferAddressType
      otherAddress: string
      venueId: string
    }
    students?: string[]
    isShowcase?: boolean
  }
  domains?: EducationalDomain[]
}
