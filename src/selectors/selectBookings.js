import get from 'lodash.get'
import moment from 'moment'
import difference from 'lodash.difference'
import { createSelector } from 'reselect'

export const selectBookings = createSelector(
  state => state.data.bookings,
  // (state, eventOrThingId) => eventOrThingId
  allBookings => allBookings
  // if (eventOrThingId) {
  //   filteredBookings = bookings.filter(booking => {
  //     // FIXME -> replace par lodash.get
  //     const { stock } = booking
  //     const { offer } = stock || {}
  //     const { eventOccurence, thingId } = offer || {}
  //     const { eventId } = eventOccurence || {}
  //
  //     if (thingId) {
  //       return thingId === eventOrThingId
  //     }
  //     return eventId === eventOrThingId
  //   })
  // }
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
  (allBookings, soonBookings) => {
    const results = difference(allBookings, soonBookings)
    const filtered = results.filter(booking => {
      const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
      return date
    })
    return filtered
  }
)

export default selectBookings
