import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, venueId) {
  return venueId || ''
}

const selectOffersByVenueId = createCachedSelector(
  state => state.data.offers || [],
  (state, venueId) => venueId,
  (offers, venueId) => offers.filter(offer => offer.venueId === venueId)
)(mapArgsToCacheKey)

export default selectOffersByVenueId
