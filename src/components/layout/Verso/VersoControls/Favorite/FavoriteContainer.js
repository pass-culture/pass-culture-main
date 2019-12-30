import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'redux-thunk-data'
import { compose } from 'redux'

import Favorite from './Favorite'
import { selectOfferByRouterMatch } from '../../../../../selectors/data/offersSelectors'
import { favoriteNormalizer } from '../../../../../utils/normalizers'
import { selectFavoriteByOfferId } from '../../../../../selectors/data/favoritesSelectors'
import { selectMediationByRouterMatch } from '../../../../../selectors/data/mediationsSelectors'

const API_PATH_TO_FAVORITES_ENDPOINT = '/favorites'

export const apiPath = (isFavorite, offerId) => {
  const chunk = isFavorite ? `/${offerId}` : ''

  return `${API_PATH_TO_FAVORITES_ENDPOINT}${chunk}`
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const mediation = selectMediationByRouterMatch(state, match) || {}
  const { id: mediationId } = mediation
  const offer = selectOfferByRouterMatch(state, match) || { id: '' }
  const { id: offerId } = offer
  const favorite = selectFavoriteByOfferId(state, offerId)
  const isFavorite = favorite !== undefined

  return {
    isFavorite,
    mediationId,
    offerId,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleFavorite: (offerId, mediationId, isFavorite, showFailModal, handleSuccess) => () => {
    dispatch(
      requestData({
        apiPath: apiPath(isFavorite, offerId),
        body: {
          mediationId,
          offerId,
        },
        handleFail: showFailModal,
        handleSuccess,
        method: isFavorite ? 'DELETE' : 'POST',
        normalizer: favoriteNormalizer,
      })
    )
  },
  loadFavorites: () => {
    dispatch(
      requestData({
        apiPath: API_PATH_TO_FAVORITES_ENDPOINT,
        normalizer: favoriteNormalizer,
      })
    )
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Favorite)
