import { IStockEventFormValues } from './types'

export const STOCK_EVENT_FORM_DEFAULT_VALUES: IStockEventFormValues = {
  stockId: undefined,
  beginningDate: null,
  beginningTime: null,
  remainingQuantity: '',
  bookingsQuantity: '',
  quantity: '',
  bookingLimitDatetime: null,
  price: '',
  isDeletable: true,
}

// 'price','quantity','bookingLimitDatetime', are editable
export const STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS = [
  'beginningDate',
  'beginningTime',
]
