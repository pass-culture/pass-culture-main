import { Quantity } from 'ui-kit/form/QuantityInput/QuantityInput'

export interface StockThingFormValues {
  stockId?: number
  remainingQuantity?: string
  bookingsQuantity?: string
  quantity?: Quantity
  bookingLimitDatetime?: string | null
  price?: number | undefined
  activationCodes?: string[]
  activationCodesExpirationDatetime?: string | null
  isDuo?: boolean
}
