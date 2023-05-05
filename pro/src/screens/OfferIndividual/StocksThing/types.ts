export interface IStockThingFormValues {
  stockId?: number
  remainingQuantity: string
  bookingsQuantity: string
  quantity: number | null | ''
  bookingLimitDatetime: Date | null
  price: number | ''
  activationCodes: string[]
  activationCodesExpirationDatetime: Date | null
  isDuo: boolean | undefined
}
