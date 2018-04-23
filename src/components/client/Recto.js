import React from 'react'
import { connect } from 'react-redux'

import Thumb from '../layout/Thumb'
import selectCurrentRecommendation from '../../selectors/currentRecommendation'
import selectNextRecommendation from '../../selectors/nextRecommendation'
import selectPreviousRecommendation from '../../selectors/previousRecommendation'
import { IS_DEV } from '../../utils/config'

const Recto = ({
  dateRead,
  mediation,
  id,
  index,
  isFlipped,
  offer,
  thumbUrl,
}) => {
  const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` }
  const thumbStyle = Object.assign({}, backgroundStyle)
  if (mediation) {
    thumbStyle.backgroundSize = 'cover'
  }
  return (
    <div className="recto">
      <Thumb src={thumbUrl} withMediation={mediation} translated={isFlipped} />
      {IS_DEV && (
        <div className="debug absolute right-0 mr2 p2">
          <span>
            {id} {offer && offer.id} {index}
          </span>
          {dateRead && [
            <span key={0}>&middot;</span>,
            <span key={1}>{dateRead}</span>,
          ]}
        </div>
      )}
    </div>
  )
}

export default connect((state, ownProps) =>
  Object.assign(
    {
      isFlipped: state.verso.isFlipped,
      recommendations: state.data.recommendations,
    },
    ownProps.position === 'current'
      ? selectCurrentRecommendation(state)
      : ownProps.position === 'previous'
        ? selectPreviousRecommendation(state)
        : ownProps.position === 'next' && selectNextRecommendation(state)
  )
)(Recto)
