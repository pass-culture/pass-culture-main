import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Thumb from './layout/Thumb'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'
import { IS_DEV } from '../utils/config'

// FIXME -> move to pass-culture-shared
const noop = () => {}

const Recto = ({ areDetailsVisible, extraClassName, recommendation }) => {
  const { dateRead, mediation, id, index, isClicked, offer, thumbUrl } =
    recommendation || {}

  const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` }
  const thumbStyle = Object.assign({}, backgroundStyle)
  if (mediation) {
    thumbStyle.backgroundSize = 'cover'
  }
  return (
    <div className={classnames('recto', extraClassName)}>
      <Thumb
        src={thumbUrl}
        withMediation={mediation}
        translated={areDetailsVisible}
      />
      {IS_DEV && (
        <div className="debug debug-recto">
          <div>
            {id} 
            {' '}
            {offer && offer.id} 
            {' '}
            {index}
          </div>
          {dateRead && <div> déjà lue </div>}
          {isClicked && <div> déjà retournée </div>}
        </div>
      )}
    </div>
  )
}

Recto.defaultProps = {
  extraClassName: null,
  recommendation: null,
}

Recto.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
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
      areDetailsVisible: state.card.areDetailsVisible,
      recommendation: recoSelector(state, offerId, mediationId),
    }
  })
)(Recto)
