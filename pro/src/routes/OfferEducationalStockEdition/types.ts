export type StockResponse = {
  id: string
  beginningDatetime?: string
  bookingLimitDatetime?: string
  price: number
  numberOfTickets?: number
  isEducationalStockEditable?: boolean
  educationalPriceDetail?: string
}
