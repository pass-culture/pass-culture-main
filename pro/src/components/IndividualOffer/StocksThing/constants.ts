import { StockThingFormValues } from './types'

export const STOCK_THING_FORM_DEFAULT_VALUES: StockThingFormValues = {
  stockId: undefined,
  remainingQuantity: 'unlimited',
  bookingsQuantity: '0',
  bookingLimitDatetime: '',
  quantity: undefined,
  price: undefined,
  activationCodes: [],
  activationCodesExpirationDatetime: '',
  isDuo: undefined,
}
