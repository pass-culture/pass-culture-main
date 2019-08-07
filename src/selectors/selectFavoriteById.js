import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, favoriteId) {
  return favoriteId || ''
}

export const selectFavoriteById = createCachedSelector(
  state => state.data.favorites,
  (state, offerId) => offerId,
  (state, mediationId) => mediationId,
  (favorites, offerId, mediationId) =>
    favorites.find(favorite => favorite.offerId === offerId && favorite.mediationId === mediationId)
)(mapArgsToCacheKey)

export default selectFavoriteById
