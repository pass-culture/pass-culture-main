import get from 'lodash.get'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.bookings,
  (state, eventOrThingId) => eventOrThingId,
  (bookings, eventOrThingId) => {
    //FIXME: this should not be necessary as initialstate is set
    if (!bookings) {
      return []
    }
    return bookings.filter(booking => {
      const stock = booking.stock
      const thingId = get(stock, 'offer.thingId')
      if (thingId) {
        return thingId === eventOrThingId
      } else {
        return get(stock, 'eventOccurence.offer.eventId') === eventOrThingId
      }
    })
  }
)
