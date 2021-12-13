export type StockPayload = {
  beginningDatetime: Date
  bookingLimitDatetime: Date | null
  totalPrice: number | ''
  numberOfTickets: number | ''
}
