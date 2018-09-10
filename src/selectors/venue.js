import get from 'lodash.get'
import createCachedSelector from 're-reselect'

export default createCachedSelector(
  state => state.data.venues,
  (state, venueId) => venueId,
  (state, venueId, offererId) => offererId,
  state => get(state, 'user.email'),
  (venues, venueId, offererId, bookingEmail) => {
    const venue = venues.find(v => v.id === venueId)
    return (
      venue &&
      Object.assign(
        {
          bookingEmail,
          managingOffererId: offererId,
        },
        venue
      )
    )
  }
)((state, venueId) => venueId || '')
