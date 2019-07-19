import get from 'lodash.get'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import Recto from './Recto'
import currentRecommendationSelector from '../../selectors/currentRecommendation/currentRecommendation'
import nextRecommendationSelector from '../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../selectors/previousRecommendation'

export const getSelectorByCardPosition = position => {
  switch (position) {
    case 'current':
      return currentRecommendationSelector
    case 'previous':
      return previousRecommendationSelector
    case 'next':
      return nextRecommendationSelector
    default:
      return () => {}
  }
}

const getRecommendationBySelectorUsingRouterParams = (state, ownProps) => {
  const position = get(ownProps, 'position')
  const { mediationId, offerId } = ownProps.match.params
  const recoSelector = getSelectorByCardPosition(position)
  return recoSelector(state, offerId, mediationId)
}

export const mapStateToProps = (state, ownProps) => {
  const areDetailsVisible = get(state, 'card.areDetailsVisible') || false

  const recommendation =
    get(ownProps, 'recommendation') || getRecommendationBySelectorUsingRouterParams(state, ownProps)

  return {
    areDetailsVisible,
    recommendation,
  }
}

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Recto)
