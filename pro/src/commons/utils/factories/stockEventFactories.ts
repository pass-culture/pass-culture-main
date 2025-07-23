/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { StockEventFormValues } from 'components/IndividualOffer/StocksEventEdition/types'

export const stockEventFactory = (
  customStockEvent: Partial<StockEventFormValues> = {}
): StockEventFormValues => ({
  stockId: 1,
  remainingQuantity: 10,
  bookingsQuantity: 1,
  bookingLimitDatetime: '2022-12-29',
  priceCategoryId: '1',
  beginningDate: '2022-12-29',
  beginningTime: '00:00',
  isDeletable: true,
  readOnlyFields: [],
  ...customStockEvent,
})
