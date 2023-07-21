import { format } from 'date-fns'

import { stockEventFactory } from 'screens/OfferIndividual/StocksEventEdition/StockFormList/stockEventFactory'
import { FORMAT_ISO_DATE_ONLY } from 'utils/date'

import { hasChangesOnStockWithBookings } from '../StocksEventEdition'

describe('hasChangesOnStockWithBookings', () => {
  it('should return false when no booking quantity', () => {
    const result = hasChangesOnStockWithBookings([], [])
    expect(result).toBe(false)
  })

  it('should return false when booking quantity is 0', () => {
    const result = hasChangesOnStockWithBookings(
      [stockEventFactory({ bookingsQuantity: 0 })],
      []
    )
    expect(result).toBe(false)
  })

  it('should return true when detecting change on price', () => {
    const result = hasChangesOnStockWithBookings(
      [stockEventFactory()],
      [stockEventFactory({ priceCategoryId: '42' })]
    )
    expect(result).toBe(true)
  })

  it('should return true when detecting change on beginningDate', () => {
    const result = hasChangesOnStockWithBookings(
      [stockEventFactory()],
      [
        stockEventFactory({
          beginningDate: format(new Date(), FORMAT_ISO_DATE_ONLY),
        }),
      ]
    )
    expect(result).toBe(true)
  })

  it('should return true when detecting change on beginningTime', () => {
    const result = hasChangesOnStockWithBookings(
      [stockEventFactory()],
      [
        stockEventFactory({
          beginningTime: format(new Date(), FORMAT_ISO_DATE_ONLY),
        }),
      ]
    )
    expect(result).toBe(true)
  })

  it('should return false when detecting change on other field', () => {
    const result = hasChangesOnStockWithBookings(
      [stockEventFactory()],
      [stockEventFactory({ bookingsQuantity: 42 })]
    )
    expect(result).toBe(false)
  })
})
