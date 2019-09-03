import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Deck from './Deck'
import selectCurrentRecommendation from '../selectors/selectCurrentRecommendation'
import selectNextRecommendation from '../selectors/selectNextRecommendation'
import selectPreviousRecommendation from '../selectors/selectPreviousRecommendation'
import selectUniqAndIndexifiedRecommendations from '../selectors/selectUniqAndIndexifiedRecommendations'
import selectMediationById from '../../../../selectors/selectMediationById'

const NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD = 5

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const { params } = match
  const { mediationId, offerId } = params

  const currentRecommendation = selectCurrentRecommendation(state, offerId, mediationId)
  const { mediationId: currentMediationId } = currentRecommendation || {}
  const currentMediation = selectMediationById(state, currentMediationId)
  const { thumbCount, tutoIndex } = currentMediation || {}

  const recommendations = selectUniqAndIndexifiedRecommendations(state)
  const nbRecos = recommendations ? recommendations.length : 0

  const isTutoWithOnlyOneThumb = typeof tutoIndex === 'number' && thumbCount <= 1
  const hasNoVerso = !currentRecommendation || isTutoWithOnlyOneThumb

  const nextLimit =
    nbRecos > 0 &&
    (NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD >= nbRecos - 1
      ? nbRecos - 1
      : nbRecos - 1 - NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD)

  const previousLimit =
    nbRecos > 0 &&
    (NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD < nbRecos - 1
      ? NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD + 1
      : 0)

  return {
    currentRecommendation,
    isEmpty: get(state, 'loading.config.isEmpty'),
    isFlipDisabled: hasNoVerso,
    nextLimit,
    nextRecommendation: selectNextRecommendation(state, offerId, mediationId),
    previousLimit,
    previousRecommendation: selectPreviousRecommendation(state, offerId, mediationId),
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
