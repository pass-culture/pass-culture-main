import createCachedSelector from 're-reselect'

import { selectVenuesByOffererId } from './data/venuesSelectors'

function mapArgsToCacheKey(state, offererId, venueId) {
  return `${offererId || ''}/${venueId || ''}`
}

const selectOffersByOffererIdAndVenueId = createCachedSelector(
  state => state.data.offers,
  (state, offererId) => offererId && selectVenuesByOffererId(state, offererId),
  (state, offererId, venueId) => venueId,
  (offers, venues, venueId) => {
    const venueIds = [].concat(venueId || (venues || []).map(v => v.id))
    return offers.filter(o => (venueIds.length ? venueIds.includes(o.venueId) : true))
  }
)(mapArgsToCacheKey)

export default selectOffersByOffererIdAndVenueId
