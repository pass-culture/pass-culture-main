import createCachedSelector from 're-reselect'

const mapArgsToCacheKey = (state, offerId) => offerId || ''

export const selectFavoriteByOfferId = createCachedSelector(
  state => state.data.favorites,
  (state, offerId) => offerId,
  (favorites, offerId) => favorites.find(favorite => favorite.offerId === offerId)
)(mapArgsToCacheKey)

export default selectFavoriteByOfferId
