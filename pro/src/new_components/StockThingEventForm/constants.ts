import { IStockThingEventFormValues } from './types'

export const STOCK_THING_EVENT_FORM_DEFAULT_VALUES: IStockThingEventFormValues =
  {
    stockId: undefined,
    remainingQuantity: '',
    bookingsQuantity: '',
    quantity: '',
    bookingLimitDatetime: null,
    price: '',
    eventTime: '',
    eventDatetime: '',
  }
