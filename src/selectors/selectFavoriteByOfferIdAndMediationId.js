import { compose } from 'redux'

import selectFavorites from './selectFavorites'

const selectFavoriteByOfferIdAndMediationId = (offerId, mediationId) =>
  compose(
    favorites =>
      favorites.find(
        favorite => favorite.offerId === offerId && favorite.mediationId === mediationId
      ),
    selectFavorites
  )

export default selectFavoriteByOfferIdAndMediationId
