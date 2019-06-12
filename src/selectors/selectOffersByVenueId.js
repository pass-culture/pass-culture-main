import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, venueId) {
  return venueId || ''
}

export const selectOffersByVenueId = createCachedSelector(
  state => state.data.offers,
  (state, venueId) => venueId,
  (offers, venueId) => offers.find(offer => offer.venueId === venueId)
)(mapArgsToCacheKey)

export default selectOffersByVenueId
