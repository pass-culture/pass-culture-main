import { IStockEventFormValues } from './types'

export const stockEventFactory = (): IStockEventFormValues => ({
  stockId: 'AA',
  remainingQuantity: '10',
  bookingsQuantity: '1',
  quantity: 11,
  bookingLimitDatetime: new Date('2022-12-29T00:00:00Z'),
  price: 66.6,
  beginningDate: new Date('2022-12-29T00:00:00Z'),
  beginningTime: new Date('2022-12-29T00:00:00Z'),
  isDeletable: true,
  readOnlyFields: [],
})
