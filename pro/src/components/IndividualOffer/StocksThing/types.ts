export interface StockThingFormValues {
  stockId?: number
  bookingLimitDatetime?: string | undefined
  activationCodesExpirationDatetime?: string | undefined
  remainingQuantity?: string | undefined
  bookingsQuantity?: string | undefined
  quantity?: number | undefined
  price?: number | undefined
  activationCodes?: string[] | undefined
  isDuo?: boolean | undefined
}
