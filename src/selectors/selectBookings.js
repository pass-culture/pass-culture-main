import get from 'lodash.get'
import moment from 'moment'
import difference from 'lodash.difference'
import { createSelector } from 'reselect'

export const selectBookings = createSelector(
  state => state.data.bookings,
  allBookings => allBookings
)

export const selectSoonBookings = createSelector(
  // select all bookings
  state => state.data.bookings,
  allBookings => {
    const twoDaysFromNow = moment().subtract(2, 'days')
    const filtered = allBookings.filter(booking => {
      const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
      if (!date) return false
      return moment(date).isSameOrBefore(twoDaysFromNow)
    })
    return filtered
  }
)

export const selectOtherBookings = createSelector(
  state => state.data.bookings,
  selectSoonBookings,
  (allBookings, soonBookings) => difference(allBookings, soonBookings)
)

export const selectBookingById = createSelector(
  state => state.data.bookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(o => o.id === bookingId)
)

export default selectBookings
