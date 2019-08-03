import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { requestData } from 'redux-saga-data'
import { compose } from 'redux'

import Favorite from './Favorite'
import getRemovedDetailsUrl from '../../../../../helpers/getRemovedDetailsUrl'
import selectFavoritesByOfferId from '../../../../../selectors/selectFavoritesByOfferId'
import selectMediationByMatch from '../../../../../selectors/selectMediationByMatch'
import selectOfferByMatch from '../../../../../selectors/selectOfferByMatch'
import selectIsFeatureDisabled from '../../../../router/selectors/selectIsFeatureDisabled'
import { favoriteNormalizer } from '../../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const isFeatureDisabled = selectIsFeatureDisabled(state, 'FAVORITE_OFFER')
  const mediation = selectMediationByMatch(state, match) || {}
  const { id: mediationId } = mediation
  const offer = selectOfferByMatch(state, match) || {}
  const { id: offerId } = offer
  const favorites = selectFavoritesByOfferId(state, offerId) || {}
  const isFavorite = favorites.length > 0
  return {
    isFavorite,
    isFeatureDisabled,
    mediationId,
    offerId
  }
}

export const mapDispatchToProps = (dispatch, ownProps) => {
  const { history, location, match } = ownProps
  const { pathname } = location

  const removeDetailsWhenFavoritesPage = isFavorite => () => {
    if (!isFavorite) {
      return
    }
    const shouldRedirectToFavorites = pathname.startsWith('/favoris')
    if (shouldRedirectToFavorites) {
      history.push(getRemovedDetailsUrl(location, match))
    }
  }

  return {
    handleFavorite: (offerId, mediationId, isFavorite, showFailModal) => () => {
      dispatch(
        requestData({
          apiPath: `/favorites${isFavorite ? `/${offerId}/${mediationId}` : ''}`,
          body: {
            mediationId,
            offerId,
          },
          handleFail: showFailModal,
          handleSuccess: removeDetailsWhenFavoritesPage(isFavorite),
          method: isFavorite ? 'DELETE' : 'POST',
          normalizer: favoriteNormalizer
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Favorite)
