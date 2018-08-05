import React from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Thumb from './layout/Thumb'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'
import { IS_DEV } from '../utils/config'

// FIXME -> move to pass-culture-shared
const noop = () => {}

const Recto = ({ isFlipped, recommendation }) => {
  const { dateRead, mediation, id, index, isClicked, offer, thumbUrl } =
    recommendation || {}

  const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` }
  const thumbStyle = Object.assign({}, backgroundStyle)
  if (mediation) {
    thumbStyle.backgroundSize = 'cover'
  }
  return (
    <div className="recto">
      <Thumb src={thumbUrl} withMediation={mediation} translated={isFlipped} />
      {IS_DEV && (
        <div className="debug debug-recto">
          <div>
            {id} 
            {' '}
            {offer && offer.id} 
            {' '}
            {index}
          </div>
          {dateRead && (
          <div>
            {' '}
déjà lue
            {' '}
          </div>
)}
          {isClicked && (
          <div>
            {' '}
déjà retournée
            {' '}
          </div>
)}
        </div>
      )}
    </div>
  )
}

Recto.defaultProps = {
  recommendation: null,
}

Recto.propTypes = {
  isFlipped: PropTypes.bool.isRequired,
  recommendation: PropTypes.object,
}

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
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const recoSelector = getSelectorByCardPosition(ownProps.position)
    return {
      isFlipped: state.verso.isFlipped,
      recommendation: recoSelector(state, offerId, mediationId),
    }
  })
)(Recto)
