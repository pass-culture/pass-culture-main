import moment from 'moment'

import { allBookingsDataset, allStocksDataset, inExactTwoDays } from './data/selectBookings'
import { filterBookingsInLessThanTwoDays } from '../selectSoonBookings'

describe('src | components | pages | my-bookings | selectors | selectSoonBookings', () => {
  describe('filterBookingsInLessThanTwoDays', () => {
    it('returns an array of bookings with beginningDatetime today or in less than 2 days', () => {
      // given
      const now = moment()
      const allBookings = allBookingsDataset()
      const stocks = allStocksDataset(now)

      // when
      const results = filterBookingsInLessThanTwoDays(stocks, allBookings, now)

      // then
      expect(results).toHaveLength(4)
      expect(
        results
          .filter(booking => booking.stock && booking.stock.beginningDatetime)
          .every(booking => booking.stock.beginningDatetime <= inExactTwoDays(now))
      ).toBe(true)
    })
  })
})
