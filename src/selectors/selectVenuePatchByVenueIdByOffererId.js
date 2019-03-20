import get from 'lodash.get'
import createCachedSelector from 're-reselect'

import selectVenueById from './selectVenueById'

function mapArgsToKey(state, venueId, offererId, bookingEmail) {
  return `${venueId || ''}/${offererId || ''}/${bookingEmail || ''}`
}

export default createCachedSelector(
  selectVenueById,
  (state, venueId, offererId) => offererId,
  state => get(state, 'form.venue.sire'),
  state => get(state, 'form.venue.name'),
  state => get(state, 'user.email'),
  (venue, offererId, sire, name, bookingEmail) => {
    const defaultData = {
      bookingEmail,
      managingOffererId: offererId,
    }

    return Object.assign(defaultData, venue)
  }
)(mapArgsToKey)
