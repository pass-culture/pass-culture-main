import { compose } from 'redux'
import createCachedSelector from 're-reselect'

export const selectFavorites = state => state.data.favorites

export const selectFavoriteById = favoriteId =>
  compose(
    favorites => favorites.find(favorite => favorite.id === favoriteId),
    selectFavorites
  )

export const selectFavoriteByOfferId = createCachedSelector(
  state => state.data.favorites,
  (state, offerId) => offerId,
  (favorites, offerId) => favorites.find(favorite => favorite.offerId === offerId)
)((state, offerId = '') => offerId)
