export type OfferEducationalStockFormValues = {
  eventDate: Date | ''
  eventTime: Date | ''
  numberOfPlaces: number | ''
  totalPrice: number | ''
  bookingLimitDatetime: Date | ''
}

export type StockPayload = {
  beginningDatetime: Date
  bookingLimitDatetime: Date | null
  totalPrice: number | ''
  numberOfTickets: number | ''
}
