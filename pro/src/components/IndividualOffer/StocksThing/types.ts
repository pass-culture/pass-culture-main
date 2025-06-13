export interface StockThingFormValues {
  stockId?: number
  remainingQuantity?: string
  bookingsQuantity?: string
  quantity?: number | null
  bookingLimitDatetime?: string | null
  price?: number | undefined
  activationCodes?: string[]
  activationCodesExpirationDatetime?: string | null
  isDuo?: boolean
}
