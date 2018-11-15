import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, offerId) => offerId || ''

export const selectOfferById = createCachedSelector(
  state => state.data.offers,
  (state, offerId) => offerId,
  (offers, offerId) => offers.find(o => o.id === offerId)
)(mapArgsToCacheKey)

export default selectOfferById
