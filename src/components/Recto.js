import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import selectCurrentUserMediation from '../selectors/currentUserMediation'
import { IS_DEV } from '../utils/config'

const Recto = ({
  dateRead,
  mediation,
  id,
  index,
  isFlipped,
  offer,
  thumbUrl
}) => {
  const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` };
  const thumbStyle = Object.assign({}, backgroundStyle);
  if (mediation) {
    thumbStyle.backgroundSize='cover';
  }
  return (
    <div className='recto'>
      <div className='background' style={backgroundStyle} />
      {
        thumbUrl && (
          <div style={thumbStyle} className={classnames('thumb', {
            translated: isFlipped
          })} />
        )
      }
      {
        IS_DEV && (
          <div className='debug absolute left-0 ml2 p2'>
            <span>
              {id} {offer && offer.id} {index}
            </span>
            {
              dateRead && [
                <span key={0}>
                  &middot;
                </span>,
                <span key={1}>
                  {dateRead}
                </span>
              ]
            }
          </div>
        )
      }
   </div>
  )
}

export default connect(
  (state, ownProps) => Object.assign({
    isFlipped: state.verso.isFlipped,
    userMediations: state.data.userMediations
  }, selectCurrentUserMediation(state))
)(Recto)
