import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Deck from './Deck'
import selectCurrentRecommendation from '../selectors/selectCurrentRecommendation'
import selectNextRecommendation from '../selectors/selectNextRecommendation'
import selectPreviousRecommendation from '../selectors/selectPreviousRecommendation'
import selectRecommendationsWithLastFakeReco from '../selectors/selectRecommendationsWithLastFakeRecommendation'
import { selectMediationById } from '../../../../selectors/data/mediationsSelectors'
import { getNextLimit } from './utils/limits'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params

  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
  const { mediationId: currentMediationId } = currentRecommendation || {}
  const currentMediation = selectMediationById(state, currentMediationId)
  const recommendations = selectRecommendationsWithLastFakeReco(state)
  const nextRecommendation = selectNextRecommendation(state, offerId, mediationId)
  const previousRecommendation = selectPreviousRecommendation(state, offerId, mediationId)

  const { thumbCount, tutoIndex } = currentMediation || {}
  const nbRecommendations = recommendations ? recommendations.length : 0
  const isTutoWithOnlyOneThumb = typeof tutoIndex === 'number' && thumbCount <= 1
  const hasNoVerso =
    !currentRecommendation || isTutoWithOnlyOneThumb || currentMediationId === 'fin'
  const nextLimit = getNextLimit(nbRecommendations)

  return {
    currentRecommendation,
    isFlipDisabled: hasNoVerso,
    nextLimit,
    nextRecommendation,
    previousRecommendation,
    recommendations,
  }
}

export const mapSizeToProps = ({ width, height }) => ({
  height,
  width: Math.min(width, 500),
})

export default compose(
  withRouter,
  withSizes(mapSizeToProps),
  connect(mapStateToProps)
)(Deck)
