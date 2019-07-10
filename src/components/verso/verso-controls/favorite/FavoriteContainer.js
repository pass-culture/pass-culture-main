import { mergeData } from 'fetch-normalize-data'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import currentRecommendationSelector from '../../../../selectors/currentRecommendation'
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

export const mapStateToProps = (state, { match: { params } }) => {
  const { mediationId, offerId } = params
  const recommendation = currentRecommendationSelector(state, offerId, mediationId) || {}

  return {
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleFavorite: (isFavorite, recommendation, showFailModal) => () => {
    dispatch(
      requestData({
        apiPath: `/offers/favorites${
          isFavorite ? `/${recommendation.offerId}/${recommendation.mediationId}` : ''
        }`,
        body: {
          mediationId: recommendation.mediationId,
          offerId: recommendation.offerId,
        },
        handleFail: showFailModal,
        handleSuccess: mergeDataWithStore(dispatch, isFavorite, recommendation),
        method: isFavorite ? 'DELETE' : 'POST',
        stateKey: 'offersFavorites',
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
