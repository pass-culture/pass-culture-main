import createCachedSelector from 're-reselect'

import selectVenuesByOffererIdAndOfferType from './selectVenuesByOffererIdAndOfferType'

function mapArgsToCacheKey(state, offererId, venueId) {
  return `${offererId || ''}/${venueId || ''}`
}

export const selectOffersByOffererIdAndVenueId = createCachedSelector(
  state => state.data.offers,
  (state, offererId) =>
    offererId && selectVenuesByOffererIdAndOfferType(state, offererId),
  (state, offererId, venueId) => venueId,
  (offers, venues, venueId) => {
    const venueIds = [].concat(venueId || (venues || []).map(v => v.id))
    return offers.filter(o =>
      venueIds.length ? venueIds.includes(o.venueId) : true
    )
  }
)(mapArgsToCacheKey)

export default selectOffersByOffererIdAndVenueId
