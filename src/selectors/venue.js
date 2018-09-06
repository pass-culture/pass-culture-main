import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import venuesSelector from './venues'

export default createCachedSelector(
  state => state.data.venues,
  (state, venueId) => venueId,
  (state, venueId, offererId) => offererId,
  state => get(state, 'user.email'),
  (venues, venueId, offererId, bookingEmail) => {
    return Object.assign(
      {
        bookingEmail,
        managingOffererId: offererId,
      },
      venues.find(v => v.id === venueId)
    )
  }
)((state, venueId) => venueId || '')
