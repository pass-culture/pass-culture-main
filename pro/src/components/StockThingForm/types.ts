export interface IStockThingFormValues {
  stockId?: string
  remainingQuantity: string
  bookingsQuantity: string
  quantity: string
  bookingLimitDatetime: Date | null
  price: string
  activationCodes: string[]
  activationCodesExpirationDatetime: Date | null
}
