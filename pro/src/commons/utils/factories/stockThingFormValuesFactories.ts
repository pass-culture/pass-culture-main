/* istanbul ignore file: Those are test helpers, their coverage is not relevant */
import { StockThingFormValues } from '@/components/IndividualOffer/StocksThing/types'

export const stockThingFormValuesFactory = (
  customStockThing: Partial<StockThingFormValues> = {}
): StockThingFormValues => ({
  stockId: 1,
  remainingQuantity: '10',
  bookingsQuantity: '1',
  quantity: 9,
  bookingLimitDatetime: '2022-12-29',
  price: 66.6,
  activationCodes: [],
  activationCodesExpirationDatetime: '',
  isDuo: undefined,
  ...customStockThing,
})
