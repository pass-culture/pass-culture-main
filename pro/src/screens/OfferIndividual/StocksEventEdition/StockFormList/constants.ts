import { StockEventFormValues, StockEventFormHiddenValues } from './types'

const STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES: StockEventFormHiddenValues = {
  stockId: undefined,
  isDeletable: true,
  readOnlyFields: [],
}

export const STOCK_EVENT_FORM_DEFAULT_VALUES: StockEventFormValues = {
  beginningDate: null,
  beginningTime: null,
  remainingQuantity: '',
  bookingsQuantity: 0,
  bookingLimitDatetime: null,
  priceCategoryId: '',
  ...STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES,
}

// 'price','quantity','bookingLimitDatetime', are editable
export const STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS: (keyof StockEventFormValues)[] =
  ['beginningDate', 'beginningTime']

// 'quantity','bookingLimitDatetime' are editable
export const STOCK_EVENT_CINEMA_PROVIDER_READ_ONLY_FIELDS: (keyof StockEventFormValues)[] =
  ['beginningDate', 'beginningTime', 'priceCategoryId']

export const STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS: (keyof StockEventFormValues)[] =
  [
    'beginningDate',
    'beginningTime',
    'remainingQuantity',
    'bookingLimitDatetime',
    'priceCategoryId',
  ]
