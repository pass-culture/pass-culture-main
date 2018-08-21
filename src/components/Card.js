import { requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Recto from './Recto'
import Verso from './Verso'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'

// FIXME -> move to pass-culture-shared
const noop = () => {}

class Card extends PureComponent {
  componentDidUpdate(prevProps) {
    const {
      isFlipped,
      recommendation,
      position,
      requestDataAction,
    } = this.props

    const isCurrent = recommendation && position === 'current'
    if (!isCurrent) return

    const shouldRequest =
      !prevProps.isFlipped && isFlipped && !recommendation.isClicked
    if (!shouldRequest) return

    const options = {
      body: { isClicked: true },
      key: 'recommendations',
    }

    requestDataAction('PATCH', `recommendations/${recommendation.id}`, options)
  }

  render() {
    const { position, recommendation, width } = this.props
    const { headerColor, index } = recommendation || {}
    const iscurrent = position === 'current'
    const translateTo = index * width
    return (
      <div
        className={`card ${iscurrent ? 'current' : ''}`}
        style={{
          backgroundColor: headerColor || '#000',
          transform: `translate(${translateTo}px, 0)`,
        }}
      >
        {iscurrent && <Verso />}
        <Recto position={position} />
      </div>
    )
  }
}

Card.defaultProps = {
  isFlipped: false,
  recommendation: null,
}

Card.propTypes = {
  isFlipped: PropTypes.bool,
  position: PropTypes.string.isRequired,
  recommendation: PropTypes.object,
  requestDataAction: PropTypes.func.isRequired,
  width: PropTypes.number.isRequired,
}

const mapSizeToProps = ({ width, height }) => ({
  height,
  width: Math.min(width, 500), // body{max-width: 500px;}
})

const getSelectorByCardPosition = position => {
  switch (position) {
    case 'current':
      return currentRecommendationSelector
    case 'previous':
      return previousRecommendationSelector
    case 'next':
      return nextRecommendationSelector
    default:
      return noop
  }
}

export default compose(
  withSizes(mapSizeToProps),
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      const recomendationSelector = getSelectorByCardPosition(ownProps.position)
      return {
        isFlipped: state.verso.isFlipped,
        recommendation: recomendationSelector(
          state,
          offerId,
          mediationId,
          ownProps.position
        ),
      }
    },
    { requestDataAction: requestData }
  )
)(Card)
