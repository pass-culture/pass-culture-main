import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import venueSelector from './venue'

export default createCachedSelector(
  venueSelector,
  (state, venueId, offererId) => offererId,
  state => get(state, 'user.email'),
  (venue, offererId, bookingEmail) => {
    return Object.assign(
      {
        bookingEmail,
        managingOffererId: offererId,
      },
      venue
    )
  }
)(
  (state, venueId, offererId, bookingEmail) =>
    `${venueId || ''}/${offererId || ''}/${bookingEmail || ''}`
)
