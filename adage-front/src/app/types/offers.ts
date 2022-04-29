export interface VenueType {
  address: string
  city: string
  coordinates: {
    latitude: number
    longitude: number
  }
  name: string
  postalCode: string
  publicName?: string
  managingOfferer: {
    name: string
  }
}

export enum ADRESS_TYPE {
  OFFERER_VENUE = 'offererVenue',
  SCHOOL = 'school',
  OTHER = 'other',
}

export interface OfferType {
  id: number
  name: string
  subcategoryLabel: string
  description?: string
  venue: VenueType
  stocks: StockType[]
  isSoldOut: boolean
  isExpired: boolean
  durationMinutes?: number
  mentalDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  extraData?: {
    contactEmail?: string
    contactPhone?: string
    offerVenue?: {
      addressType: ADRESS_TYPE
      otherAddress: string
      venueId: string
    }
    students?: string[]
    isShowcase?: boolean
  }
}

export interface VenueFilterType {
  id: number
  name: string
  publicName?: string
}

export interface StockType {
  id: number
  beginningDatetime: Date
  bookingLimitDatetime: Date
  isBookable: boolean
  price: number
  numberOfTickets?: number
  educationalPriceDetail?: string
}

export type CollectiveOfferBaseModel = {
  id: number
  subcategoryLabel: string
  description?: string
  isExpired: boolean
  isSoldOut: boolean
  name: string
  venue: VenueType
  students: string[]
  offerVenue: {
    addressType: ADRESS_TYPE
    otherAddress: string
    venueId: string
  }
  contactEmail: string
  contactPhone: string
  durationMinutes?: number
  motorDisabilityCompliant: boolean
  visualDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  offerId?: string
  educationalPriceDetail?: string
}

export type CollectiveOffer = CollectiveOfferBaseModel & {
  stock: StockType
}

export type CollectiveOfferTemplate = CollectiveOfferBaseModel
