import createCachedSelector from 're-reselect'

function mapArgsToCacheKey(state, favoriteId) {
  return favoriteId || ''
}

export const selectFavoriteById = createCachedSelector(
  state => state.data.favorites,
  (state, favoriteId) => favoriteId,
  (favorites, favoriteId) => favorites.find(favorite => favorite.id === favoriteId)
)(mapArgsToCacheKey)

export default selectFavoriteById
