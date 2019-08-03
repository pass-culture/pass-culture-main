import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, offerId) {
  return offerId || ''
}

export const selectOfferById = createCachedSelector(
  state => state.data.offers,
  (state, offerId) => offerId,
  (offers, offerId) => offers.find(offer => offer.id === offerId)
)(mapArgsToCacheKey)

export default selectOfferById
