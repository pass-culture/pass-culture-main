import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'redux-saga-data'
import { compose } from 'redux'

import Favorite from './Favorite'
import selectFavoriteByOfferId from '../../../../../selectors/selectFavoritesByOfferId'
import selectMediationByRouterMatch from '../../../../../selectors/selectMediationByRouterMatch'
import selectOfferByRouterMatch from '../../../../../selectors/selectOfferByRouterMatch'
import selectIsFeatureDisabled from '../../../../router/selectors/selectIsFeatureDisabled'
import { favoriteNormalizer } from '../../../../../utils/normalizers'

const API_PATH_TO_FAVORITES_ENDPOINT = '/favorites'
export const apiPath = (isFavorite, offerId, mediationId) => {
  const url = API_PATH_TO_FAVORITES_ENDPOINT

  if (isFavorite) {
    if (mediationId) {
      return `${url}/${offerId}/${mediationId}`
    }

    return `${url}/${offerId}`
  }

  return url
}

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const isFeatureDisabled = selectIsFeatureDisabled(state, 'FAVORITE_OFFER')
  const mediation = selectMediationByRouterMatch(state, match) || {}
  const { id: mediationId = null } = mediation
  const offer = selectOfferByRouterMatch(state, match) || {}
  const { id: offerId } = offer

  const favorite = selectFavoriteByOfferId(state, offerId)
  const isFavorite = favorite !== undefined

  return {
    isFavorite,
    isFeatureDisabled,
    mediationId,
    offerId,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleFavorite: (offerId, mediationId, isFavorite, showFailModal) => () => {
    dispatch(
      requestData({
        apiPath: apiPath(isFavorite, offerId, mediationId),
        body: {
          mediationId,
          offerId,
        },
        handleFail: showFailModal,
        method: isFavorite ? 'DELETE' : 'POST',
        normalizer: favoriteNormalizer,
      })
    )
  },
  loadFavorites: () => {
    dispatch(
      requestData({
        apiPath: API_PATH_TO_FAVORITES_ENDPOINT,
        method: 'GET',
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
