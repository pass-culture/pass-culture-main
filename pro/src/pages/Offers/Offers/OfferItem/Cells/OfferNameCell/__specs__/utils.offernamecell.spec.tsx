import { collectiveBookingCollectiveStockFactory } from 'utils/collectiveApiFactories'

import { getRemainingTime, getDate, shouldDisplayWarning } from '../utils'

describe('Utils OfferNameCell', () => {
  it('should display no warning when the limit date is in more than 7 days', () => {
    const stock = collectiveBookingCollectiveStockFactory({
      bookingLimitDatetime: '2030-01-01T00:00:00Z',
    })
    expect(getRemainingTime(stock) >= 7).toBeTruthy()
    expect(shouldDisplayWarning(stock)).toBeFalsy()
  })

  it('should display a warning when the limit date is in less than 7 days', () => {
    const date = new Date()
    date.setDate(date.getDate() + 3)
    const stock = collectiveBookingCollectiveStockFactory({
      bookingLimitDatetime: date.toString(),
    })

    expect(getRemainingTime(stock) >= 0).toBeTruthy()
    expect(shouldDisplayWarning(stock)).toBeTruthy()
  })

  it('should return date to format dd/mm/yyyy', () => {
    const date = getDate(
      collectiveBookingCollectiveStockFactory({
        bookingLimitDatetime: '2030-01-01T00:00:00Z',
      })
    )
    expect(date).toBe('01/01/2030')
  })
})
