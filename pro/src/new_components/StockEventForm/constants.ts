import { IStockEventFormValues } from './types'

export const STOCK_EVENT_FORM_DEFAULT_VALUES: IStockEventFormValues = {
  stockId: undefined,
  beginningDate: '',
  beginningTime: '',
  remainingQuantity: '',
  bookingsQuantity: '',
  quantity: '',
  bookingLimitDatetime: null,
  price: '',
}
