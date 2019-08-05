import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'redux-saga-data'
import { compose } from 'redux'

import Favorite from './Favorite'
import selectFavoritesByOfferId from '../../../../../selectors/selectFavoritesByOfferId'
import selectMediationByMatch from '../../../../../selectors/selectMediationByMatch'
import selectOfferByMatch from '../../../../../selectors/selectOfferByMatch'
import selectIsFeatureDisabled from '../../../../router/selectors/selectIsFeatureDisabled'
import { favoriteNormalizer } from '../../../../../utils/normalizers'

export const apiPath = (isFavorite, offerId, mediationId) => {
  const url = '/favorites'

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
  const mediation = selectMediationByMatch(state, match) || {}
  const { id: mediationId = null } = mediation
  const offer = selectOfferByMatch(state, match) || {}
  const { id: offerId } = offer
  const favorites = selectFavoritesByOfferId(state, offerId) || {}
  const isFavorite = favorites.length > 0

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
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Favorite)
