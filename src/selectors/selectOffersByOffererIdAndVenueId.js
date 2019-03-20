import createCachedSelector from 're-reselect'

import venuesSelector from './venues'

function mapArgToKey(state, offererId, venueId) {
  return `${offererId || ''}/${venueId || ''}`
}

export const selectOffersByOffererIdAndVenueId = createCachedSelector(
  state => state.data.offers,
  (state, offererId, venueId) => offererId && venuesSelector(state, offererId),
  (state, offererId, venueId) => venueId,
  (offers, venues, venueId) => {
    const venueIds = [].concat(venueId || (venues || []).map(v => v.id))
    return offers.filter(o =>
      venueIds.length ? venueIds.includes(o.venueId) : true
    )
  }
)(mapArgToKey)

export default selectOffersByOffererIdAndVenueId
