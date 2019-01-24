import get from 'lodash.get'
import moment from 'moment'
import { createSelector } from 'reselect'

export const filterBookingsActivationOfTypeThing = bookingobj => {
  const offer = get(bookingobj, 'stock.resolvedOffer')
  if (!offer) return false
  const offerType = get(offer, 'eventOrThing.type')
  if (!offerType) return false
  const isActivationType = offerType === 'EventType.ACTIVATION'
  if (!isActivationType) return true
  const offerThingId = get(offer, 'thingId')
  return !offerThingId
}

export const filterBookingsInLessThanTwoDays = (
  allBookings,
  momentNowMock = null
) => {
  const twoDaysFromNow = (momentNowMock || moment()).add(2, 'days')
  const filtered = allBookings
    .filter(booking => {
      const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
      if (!date) return false
      return moment(date).isSameOrBefore(twoDaysFromNow)
    })
    .filter(filterBookingsActivationOfTypeThing)
  return filtered
}

export const filterBookingsInMoreThanTwoDays = (allBookings, momentNowMock) => {
  const twoDaysFromNow = (momentNowMock || moment()).add(2, 'days')
  const filtered = allBookings
    .filter(booking => {
      const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
      if (!date) return false
      return moment(date).isAfter(twoDaysFromNow)
    })
    .filter(filterBookingsActivationOfTypeThing)
  return filtered
}

export const removePastBookings = (allbookings, momentNowMock = null) => {
  const now = momentNowMock || moment()
  return allbookings.filter(booking => {
    const date = get(booking, 'stock.eventOccurrence.beginningDatetime')
    if (!date) return false
    return moment(date).isSameOrAfter(now)
  })
}

export const selectBookings = createSelector(
  state => state.data.bookings,
  removePastBookings
)

export const selectSoonBookings = createSelector(
  selectBookings,
  filterBookingsInLessThanTwoDays
)

export const selectOtherBookings = createSelector(
  selectBookings,
  filterBookingsInMoreThanTwoDays
)

export const selectBookingById = createSelector(
  state => state.data.bookings,
  (state, bookingId) => bookingId,
  (bookings, bookingId) => bookings.find(o => o.id === bookingId)
)

export default selectBookings
