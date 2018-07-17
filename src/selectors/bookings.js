import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.bookings,
  (state, recommendationId) => recommendationId,
  (bookings, eventOrThingId) => {
    return bookings.filter(function (booking) {
        const offer = booking.offer
        console.log("offer", offer)
        if (offer.thingId) {
          return offer.thingId === eventOrThingId
        } else {
          return offer.eventOccurence.eventId === eventOrThingId
        }
    })
  }
)
