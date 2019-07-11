import get from 'lodash.get'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import VersoButtonFavorite from './VersoButtonFavorite'
import currentRecommendationSelector from '../../../../selectors/currentRecommendation'

const checkIsFavorite = recommendation => {
  const result = get(recommendation, 'isFavorite')
  return result || false
}

const getRecommendationId = recommendation => {
  const result = get(recommendation, 'id')
  return result || null
}

export const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const isFavorite = checkIsFavorite(recommendation)
  const recommendationId = getRecommendationId(recommendation)
  return {
    isFavorite,
    recommendationId,
  }
}

export const mapDispatchToProps = () => ({
  onClick: () => () => {
    // TODO: pas encore implémenté
    // if (!recommendationId) return;
    // const apiPath = `/currentRecommendations/${recommendationId}`;
    // dispatch(
    //   requestData({
    //     apiPath,
    //     body: { isFavorite: !isFavorite },
    //     method: 'PATCH',
    //     stateKey: 'currentRecommendations',
    //   })
    // );
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(VersoButtonFavorite)
