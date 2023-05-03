import { IStockThingFormValues } from './types'

export const STOCK_THING_FORM_DEFAULT_VALUES: IStockThingFormValues = {
  stockId: undefined,
  remainingQuantity: 'unlimited',
  bookingsQuantity: '0',
  quantity: '',
  bookingLimitDatetime: null,
  price: '',
  activationCodes: [],
  activationCodesExpirationDatetime: null,
  isDuo: undefined,
}
