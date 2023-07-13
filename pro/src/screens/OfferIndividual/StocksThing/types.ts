export interface StockThingFormValues {
  stockId?: number
  remainingQuantity: string
  bookingsQuantity: string
  quantity: number | null | ''
  bookingLimitDatetime: string
  price: number | ''
  activationCodes: string[]
  activationCodesExpirationDatetime: string
  isDuo: boolean | undefined
}
