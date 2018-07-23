import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.bookings,
  (state, recommendationId) => recommendationId,
  (bookings, eventOrThingId) => {
    //FIXME: this should not be necessary as initialstate is set
    if (!bookings) {
      return []
    }
    return bookings.filter(function (booking) {
        const offer = booking.offer
        if (offer.thingId) {
          return offer.thingId === eventOrThingId
        } else {
          return offer.eventOccurence.eventId === eventOrThingId
        }
    })
  }
)
