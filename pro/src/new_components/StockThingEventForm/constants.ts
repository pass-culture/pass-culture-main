import { IStockThingEventFormValuesArray } from './types'

export const STOCK_THING_EVENT_FORM_DEFAULT_VALUES: IStockThingEventFormValuesArray =
  {
    events: [
      {
        stockId: undefined,
        remainingQuantity: '',
        bookingsQuantity: '',
        quantity: '',
        bookingLimitDatetime: null,
        price: '',
        eventDate: '',
        eventDatetime: '',
      },
    ],
  }
