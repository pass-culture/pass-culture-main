import get from 'lodash.get'
import moment from 'moment'
import difference from 'lodash.difference'
import { createSelector } from 'reselect'

const filterBookingsActivationOfTypeThing = bookingobj => {
  const offer = get(bookingobj, 'stock.resolvedOffer')
  const offerType = get(offer, 'eventOrThing.type')
  const isActivationType = offerType === 'EventType.ACTIVATION'
  if (!isActivationType) return true
  const offerThingId = get(offer, 'thingId')
  return !offerThingId
}

export const selectBookings = createSelector(
  state => state.data.bookings,
  allBookings => allBookings
)

export const selectSoonBookings = createSelector(
  // select all bookings
  selectBookings,
  allBookings => {
    const twoDaysFromNow = moment().subtract(2, 'days')
    const filtered = allBookings
      .filter(booking => {
        const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
        if (!date) return false
        return moment(date).isSameOrBefore(twoDaysFromNow)
      })
      .filter(filterBookingsActivationOfTypeThing)
    return filtered
  }
)

export const selectOtherBookings = createSelector(
  selectBookings,
  selectSoonBookings,
  (allBookings, soonBookings) => {
    const filtered = difference(allBookings, soonBookings).filter(
      filterBookingsActivationOfTypeThing
    )
    return filtered
  }
)

export const selectBookingById = createSelector(
  state => state.data.bookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(o => o.id === bookingId)
)

export default selectBookings
