import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Price from './Price'
import Finishable from './layout/Finishable'
import distanceSelector from '../selectors/distance'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import isCurrentTutoSelector from '../selectors/isCurrentTuto'
import isFinishedSelector from '../selectors/isFinished'

const Clue = ({
  currentRecommendation,
  distance,
  isHidden,
  transitionTimeout,
  isCurrentTuto,
  isFinished,
}) => {
  const {
    offer
  } = (currentRecommendation || {})
  const {
    price
  } = (offer || {})
  return (
    <div
      className="clue"
      style={{ transition: `opacity ${transitionTimeout}ms` }}
    >
      <Finishable
        finished={
          isFinished && !isCurrentTuto // Hard coded to prevent a weird bug to arise, should be eventually removed
        }
      >
        <Price value={price} />
        <div className="separator">
          {offer ? '\u00B7' : ' '}
        </div>
        <div>
          {offer ? distance : ' '}
        </div>
      </Finishable>
    </div>
  )
}

Clue.defaultProps = {
  transitionTimeout: 250,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    return {
      currentRecommendation: currentRecommendationSelector(state, offerId, mediationId),
      distance: distanceSelector(state),
      isCurrentTuto: isCurrentTutoSelector(state),
      isFinished: isFinishedSelector(state),
      isFlipped: state.verso.isFlipped,
    }
  })
)(Clue)
