import moment from 'moment'

import { allBookingsDataset, inExactTwoDays } from './data/selectBookings'
import { filterBookingsInMoreThanTwoDaysOrPast } from '../selectOtherBookings'

describe('filterBookingsInMoreThanTwoDaysOrPast', () => {
  it('returns all bookings excepts >= today hh:mm:s', () => {
    // given
    const now = moment()
    const allBookings = allBookingsDataset(now)

    // when
    const results = filterBookingsInMoreThanTwoDaysOrPast(allBookings, now)

    // then
    expect(results).toHaveLength(6)
    expect(
      results
        .filter(booking => booking.stock && booking.stock.beginningDatetime)
        .every(booking => {
          const date = booking.stock.beginningDatetime
          return date > inExactTwoDays(now) || date < now
        })
    ).toBe(true)
  })
})
