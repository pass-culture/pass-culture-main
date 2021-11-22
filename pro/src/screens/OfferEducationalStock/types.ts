import { OfferStatus } from './constants/offerStatus'

export type OfferEducationalStockFormValues = {
  eventDate: Date
  eventTime: string
  numberOfPlaces: number | ''
  totalPrice: number | ''
  bookingLimitDatetime: Date
}

export type Offer = {
  id: string
  status: OfferStatus
}
