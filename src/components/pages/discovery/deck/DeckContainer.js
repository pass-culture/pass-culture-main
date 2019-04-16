import get from 'lodash.get'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'
import { NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD } from '../../../../helpers/isRecommendationOfferFinished'
import currentRecommendationSelector from '../../../../selectors/currentRecommendation'
import nextRecommendationSelector from '../../../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../../../selectors/previousRecommendation'
import selectRecommendationsForDiscovery from '../../../../selectors/recommendations'
import Deck from './Deck'

export const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const { mediation } = currentRecommendation || {}
  const { thumbCount, tutoIndex } = mediation || {}

  const recommendations = selectRecommendationsForDiscovery(state)
  const nbRecos = recommendations ? recommendations.length : 0

  const isFlipDisabled =
    !currentRecommendation || (typeof tutoIndex === 'number' && thumbCount <= 1)

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
    areDetailsVisible: state.card.areDetailsVisible,
    currentRecommendation,
    draggable: state.card.draggable,
    isEmpty: get(state, 'loading.config.isEmpty'),
    isFlipDisabled,
    nextLimit,
    nextRecommendation: nextRecommendationSelector(state, offerId, mediationId),
    previousLimit,
    previousRecommendation: previousRecommendationSelector(
      state,
      offerId,
      mediationId
    ),
    recommendations,
    unFlippable: state.card.unFlippable,
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
