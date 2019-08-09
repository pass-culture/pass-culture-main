import { compose } from 'redux'

import selectFavorites from './selectFavorites'

const selectFavoriteById = favoriteId =>
  compose(
    favorites => favorites.find(favorite => favorite.id === favoriteId),
    selectFavorites
  )

export default selectFavoriteById
