import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import recommendationsSelector from '../selectors/recommendations'
import { PREVIOUS_NEXT_LIMIT } from '../utils/deck'

const DeckDebugger = ({
  nextLimit,
  previousLimit,
  isLoadingAfter,
  isLoadingBefore,
  recommendations,
  currentRecommendation,
}) => (
  <div className="debug debug-deck">
    {`(${isLoadingBefore ? '?' : ' '} ${previousLimit})`}
    {' '}
    {currentRecommendation &&
      currentRecommendation.mediation &&
      currentRecommendation.mediation.id}
    {' '}
    {currentRecommendation && currentRecommendation.index}
    {' '}
    {`(${nextLimit} ${isLoadingAfter ? '?' : ' '}) / `}
    {' '}
    {recommendations && recommendations.length - 1}
  </div>
)

DeckDebugger.defaultProps = {
  currentRecommendation: null,
  isLoadingAfter: false,
  isLoadingBefore: false,
}

DeckDebugger.propTypes = {
  currentRecommendation: PropTypes.object,
  isLoadingAfter: PropTypes.bool,
  isLoadingBefore: PropTypes.bool,
  nextLimit: PropTypes.number.isRequired,
  previousLimit: PropTypes.number.isRequired,
  recommendations: PropTypes.array.isRequired,
}

const mapStateToProps = state => {
  const recommendations = recommendationsSelector(state)
  return {
    nextLimit:
      recommendations &&
      (PREVIOUS_NEXT_LIMIT >= recommendations.length - 1
        ? recommendations.length - 1
        : recommendations.length - 1 - PREVIOUS_NEXT_LIMIT),
    previousLimit:
      recommendations &&
      (PREVIOUS_NEXT_LIMIT < recommendations.length - 1
        ? PREVIOUS_NEXT_LIMIT + 1
        : 0),
    recommendations,
  }
}

export default connect(mapStateToProps)(DeckDebugger)
