import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Thumb from './layout/Thumb'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'
import { IS_DEV } from '../utils/config'

const Recto = ({
  isFlipped,
  recommendation,
}) => {
  const {
    dateRead,
    mediation,
    id,
    index,
    isClicked,
    offer,
    thumbUrl,
  } = (recommendation || {})

  console.log('thumbUrl', thumbUrl)

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
            {id} {offer && offer.id} {index}
          </div>
          {dateRead && <div> déjà lue </div>}
          {isClicked && <div> déjà retournée </div>}
        </div>
      )}
    </div>
  )
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    return {
      isFlipped: state.verso.isFlipped,
      recommendation: ownProps.position === 'current'
        ? currentRecommendationSelector(state, offerId, mediationId)
        : ownProps.position === 'previous'
          ? previousRecommendationSelector(state, offerId, mediationId)
          : ownProps.position === 'next' && nextRecommendationSelector(state, offerId, mediationId)
    }
  })
)(Recto)
