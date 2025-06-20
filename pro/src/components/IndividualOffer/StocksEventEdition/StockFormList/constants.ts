import { StockEventFormValues, StockEventFormHiddenValues } from './types'

const STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES: StockEventFormHiddenValues = {
  stockId: 0,
  isDeletable: true,
  readOnlyFields: [],
}

export const STOCK_EVENT_FORM_DEFAULT_VALUES: StockEventFormValues = {
  beginningDate: '',
  beginningTime: '',
  remainingQuantity: null,
  bookingsQuantity: 0,
  bookingLimitDatetime: '',
  priceCategoryId: '',
  ...STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES,
}

// 'price','quantity','bookingLimitDatetime', are editable
export const STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS: (keyof StockEventFormValues)[] =
  ['beginningDate', 'beginningTime']

// 'quantity','bookingLimitDatetime' are editable
export const STOCK_EVENT_CINEMA_PROVIDER_READ_ONLY_FIELDS: (keyof StockEventFormValues)[] =
  ['beginningDate', 'beginningTime', 'priceCategoryId']
