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
        const {
          stock
        } = booking
        const {
          offer
        } = (stock || {})
        const {
          eventOccurence,
          thingId
        } = (offer || {})
        const {
          eventId
        } = (eventOccurence || {})

        if (thingId) {
          return thingId === eventOrThingId
        }
        return eventId === eventOrThingId
      })
    }

    // add dates
    filteredBookings = filteredBookings.filter(booking => {
      const {
        offer,
      } = booking
      const {
        eventOccurence
      } = (offer || {})
      const { beginningDatetime } = (eventOccurence || {})

      return Object.assign({
        date: moment(beginningDatetime)
      })
    })

    // sort
    const twoDaysFromNow = moment().subtract(2, 'days')
    filteredBookings.sort((b1, b2) => b1.date - b2.date)
      .reduce((result, booking) => {
          const isSoon = booking.date < twoDaysFromNow
          return {
            soonBookings: result.soonBookings.concat(isSoon ? booking : []),
            otherBookings: result.otherBookings.concat(isSoon ? [] : booking),
          }
        },
        {
          soonBookings: [],
          otherBookings: [],
        })

    // return
    return filteredBookings
  }
)
