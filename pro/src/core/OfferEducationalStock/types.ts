import { OfferStatus } from '../../screens/OfferEducationalStock/constants/offerStatus'

export type OfferEducationalStockFormValues = {
  eventDate: string
  eventTime: string
  numberOfPlaces: string
  totalPrice: string
  bookingLimitDatetime: string
}

export type Offer = {
  id: string
  status: OfferStatus
  venue: Venue
}

type Venue = {
  departementCode: string
}
