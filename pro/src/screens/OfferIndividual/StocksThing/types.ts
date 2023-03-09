export interface IStockThingFormValues {
  stockId?: string
  remainingQuantity: string
  bookingsQuantity: string
  quantity: number | null | ''
  bookingLimitDatetime: Date | null
  price: number | ''
  activationCodes: string[]
  activationCodesExpirationDatetime: Date | null
}
