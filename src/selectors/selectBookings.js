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
  selectBookings,
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
  selectBookings,
  selectSoonBookings,
  (allBookings, soonBookings) => difference(allBookings, soonBookings)
)

export default selectBookings
