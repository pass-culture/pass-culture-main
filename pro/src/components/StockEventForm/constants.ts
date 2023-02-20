import { IStockEventFormValues, IStockEventFormHiddenValues } from './types'

const STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES: IStockEventFormHiddenValues = {
  stockId: undefined,
  isDeletable: true,
  readOnlyFields: [],
}

export const STOCK_EVENT_FORM_DEFAULT_VALUES: IStockEventFormValues = {
  beginningDate: null,
  beginningTime: null,
  remainingQuantity: '',
  bookingsQuantity: 0,
  bookingLimitDatetime: null,
  price: '',
  priceCategoryId: '',
  ...STOCK_EVENT_FORM_DEFAULT_HIDDEN_VALUES,
}

// 'price','quantity','bookingLimitDatetime', are editable
export const STOCK_EVENT_ALLOCINE_READ_ONLY_FIELDS: (keyof IStockEventFormValues)[] =
  ['beginningDate', 'beginningTime']

// 'quantity','bookingLimitDatetime' are editable
export const STOCK_EVENT_CINEMA_PROVIDER_READ_ONLY_FIELDS: (keyof IStockEventFormValues)[] =
  ['beginningDate', 'beginningTime', 'price']

export const STOCK_EVENT_EDITION_EMPTY_SYNCHRONIZED_READ_ONLY_FIELDS: (keyof IStockEventFormValues)[] =
  [
    'beginningDate',
    'beginningTime',
    'price',
    'remainingQuantity',
    'bookingLimitDatetime',
  ]
