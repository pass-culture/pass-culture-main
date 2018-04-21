import React from 'react'
import { connect } from 'react-redux'

import Thumb from './Thumb'

import selectCurrentUserMediation from '../selectors/currentUserMediation'
import selectNextUserMediation from '../selectors/nextUserMediation'
import selectPreviousUserMediation from '../selectors/previousUserMediation'
import { IS_DEV } from '../utils/config'

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
        <div className="debug absolute left-0 ml2 p2">
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
      userMediations: state.data.userMediations,
    },
    ownProps.position === 'current'
      ? selectCurrentUserMediation(state)
      : ownProps.position === 'previous'
        ? selectPreviousUserMediation(state)
        : ownProps.position === 'next' && selectNextUserMediation(state)
  )
)(Recto)
