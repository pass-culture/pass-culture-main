import { StockThingFormValues } from './types'

export const STOCK_THING_FORM_DEFAULT_VALUES: StockThingFormValues = {
  stockId: undefined,
  remainingQuantity: 'unlimited',
  bookingsQuantity: '0',
  quantity: null,
  bookingLimitDatetime: undefined,
  price: undefined,
  activationCodes: [],
  activationCodesExpirationDatetime: '',
  isDuo: undefined,
}
