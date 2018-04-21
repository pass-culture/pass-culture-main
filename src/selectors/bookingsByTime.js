import get from 'lodash.get'
import { createSelector } from 'reselect'

import selectBookingsWithThumbUrl from './bookingsWithThumbUrl'

const getDate = booking =>
  get(booking, 'offer.eventOccurence.beginningDatetime')

export default createSelector(selectBookingsWithThumbUrl, bookings => {
  const twoDaysFromNow = new Date(
    new Date().getTime() + 2 * 24 * 60 * 60 * 1000
  )
  return bookings.sort((b1, b2) => getDate(b1) - getDate(b2)).reduce(
    (result, booking) => {
      const isSoon = getDate(booking) < twoDaysFromNow
      return {
        soonBookings: result.soonBookings.concat(isSoon ? booking : []),
        otherBookings: result.otherBookings.concat(isSoon ? [] : booking),
      }
    },
    {
      soonBookings: [],
      otherBookings: [],
    }
  )
})
