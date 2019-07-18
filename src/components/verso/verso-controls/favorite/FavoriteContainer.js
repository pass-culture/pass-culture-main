import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { mergeData, requestData } from 'redux-saga-data'

import selectIsFeatureDisabled from '../../../router/selectors/selectIsFeatureDisabled'
import currentRecommendationSelector from '../../../../selectors/currentRecommendation/currentRecommendation'
import Favorite from './Favorite'

export const mergeDataWithStore = (dispatch, isFavorite, recommendation) => (state, action) => {
  dispatch(
    mergeData({
      recommendations: [
        {
          ...recommendation,
          offer: {
            ...recommendation.offer,
            favorites: isFavorite ? [] : [action.payload.datum],
          },
        },
      ],
    })
  )
}

export const mapStateToProps = (state, ownProps) => {
  const {
    match: { params },
  } = ownProps
  const { mediationId, offerId } = params
  const isFeatureDisabled = selectIsFeatureDisabled(state, 'FAVORITE_OFFER')
  const recommendation = currentRecommendationSelector(state, offerId, mediationId) || {}
  return {
    isFeatureDisabled,
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleFavorite: (isFavorite, recommendation, showFailModal) => () => {
    dispatch(
      requestData({
        apiPath: `/favorites${
          isFavorite ? `/${recommendation.offerId}/${recommendation.mediationId}` : ''
        }`,
        body: {
          mediationId: recommendation.mediationId,
          offerId: recommendation.offerId,
        },
        handleFail: showFailModal,
        handleSuccess: mergeDataWithStore(dispatch, isFavorite, recommendation),
        method: isFavorite ? 'DELETE' : 'POST',
        stateKey: 'favorites',
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
