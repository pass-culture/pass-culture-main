import { StockThingFormValues } from './types'

export const STOCK_THING_FORM_DEFAULT_VALUES: StockThingFormValues = {
  stockId: undefined,
  remainingQuantity: 'unlimited',
  bookingsQuantity: '0',
  quantity: '',
  bookingLimitDatetime: '',
  price: '',
  activationCodes: [],
  activationCodesExpirationDatetime: '',
  isDuo: undefined,
}
