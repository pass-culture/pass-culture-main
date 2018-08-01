import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'

import selectNextLimit from '../../selectors/nextLimit'
import selectPreviousLimit from '../../selectors/previousLimit'

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
  isLoadingAfter: false,
  isLoadingBefore: false,
  currentRecommendation: null,
}

DeckDebugger.propTypes = {
  isLoadingAfter: PropTypes.bool,
  isLoadingBefore: PropTypes.bool,
  currentRecommendation: PropTypes.object,
  nextLimit: PropTypes.number.isRequired,
  previousLimit: PropTypes.number.isRequired,
  recommendations: PropTypes.array.isRequired,
}

const mapStateToProps = state => ({
  nextLimit: selectNextLimit(state),
  previousLimit: selectPreviousLimit(state),
  recommendations: state.data.recommendations || [],
})

export default connect(mapStateToProps)(DeckDebugger)
