export interface IStockEventFormValues {
  stockId?: string
  remainingQuantity: string
  bookingsQuantity: string
  quantity: string
  bookingLimitDatetime: Date | null
  price: string
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
  isDeletable: boolean
}
