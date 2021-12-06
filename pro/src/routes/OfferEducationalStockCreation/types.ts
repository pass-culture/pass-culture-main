export type StockCreationPayload = {
  offerId: string
  beginningDatetime: Date
  bookingLimitDatetime: Date | null
  totalPrice: string
  numberOfTickets: string
}
