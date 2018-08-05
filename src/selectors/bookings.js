import moment from 'moment'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.bookings,
  (state, eventOrThingId) => eventOrThingId,
  (bookings, eventOrThingId) => {
    let filteredBookings = bookings

    // by eventOrThingId
    if (eventOrThingId) {
      filteredBookings = bookings.filter(booking => {
        const { stock } = booking
        const { offer } = stock || {}
        const { eventOccurence, thingId } = offer || {}
        const { eventId } = eventOccurence || {}

        if (thingId) {
          return thingId === eventOrThingId
        }
        return eventId === eventOrThingId
      })
    }

    // add dates
    const twoDaysFromNow = moment().subtract(2, 'days')
    filteredBookings = filteredBookings.filter(booking => {
      const { offer } = booking
      const { eventOccurence } = offer || {}
      const { beginningDatetime } = eventOccurence || {}

      const date = moment(beginningDatetime)

      return Object.assign({
        date,
        isSoon: date < twoDaysFromNow,
      })
    })

    // return
    return filteredBookings
  }
)
