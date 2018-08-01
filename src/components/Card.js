import PropTypes from 'prop-types'
import get from 'lodash.get'
import { requestData } from 'pass-culture-shared'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Recto from './Recto'
import Verso from './Verso'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'

class Card extends PureComponent {
  componentDidUpdate (prevProps) {
    const {
      isFlipped,
      recommendation,
      position,
      requestDataAction
    } = this.props

    const isCurrent = recommendation && position === 'current'
    if (!isCurrent) return

    const shouldRequest =
      !prevProps.isFlipped && isFlipped && !recommendation.isClicked
    if (!shouldRequest) return

    const options = {
      key: 'recommendations',
      body: { isClicked: true }
    }

    requestDataAction('PATCH', `recommendations/${recommendation.id}`, options)
  }

  render() {
    const {
      position,
      recommendation,
      width
    } = this.props
    const {
      headerColor,
      index
    } = (recommendation || {})
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
  recommendation: null
}

Card.propTypes = {
  isFlipped: PropTypes.bool,
  recommendation: PropTypes.object,
  width: PropTypes.number.isRequired,
  position: PropTypes.string.isRequired,
  requestDataAction: PropTypes.func.isRequired,
}

const mapSizeToProps = ({ width, height }) => ({
  width: Math.min(width, 500), // body{max-width: 500px;}
  height,
})

export default compose(
  withSizes(mapSizeToProps),
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      return {
        recommendation: ownProps.position === 'current'
          ? currentRecommendationSelector(state, offerId, mediationId)
          : ownProps.position === 'previous'
            ? previousRecommendationSelector(state, offerId, mediationId)
            : ownProps.position === 'next' && nextRecommendationSelector(state, offerId, mediationId),
        isFlipped: state.verso.isFlipped,
      }
    },
    { requestDataAction: requestData }
  )
)(Card)
