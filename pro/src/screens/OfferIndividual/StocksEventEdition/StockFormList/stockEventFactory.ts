/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { IStockEventFormValues } from './types'

export const stockEventFactory = (
  customStockEvent: Partial<IStockEventFormValues> = {}
): IStockEventFormValues => ({
  stockId: 1,
  remainingQuantity: 10,
  bookingsQuantity: 1,
  bookingLimitDatetime: new Date('2022-12-29T00:00:00Z'),
  priceCategoryId: '1',
  beginningDate: new Date('2022-12-29T00:00:00Z'),
  beginningTime: new Date('2022-12-29T00:00:00Z'),
  isDeletable: true,
  readOnlyFields: [],
  ...customStockEvent,
})
