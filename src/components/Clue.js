import React from 'react'
import { connect } from 'react-redux'

import Price from './Price'
import Finishable from './layout/Finishable'
import selectDistance from '../selectors/distance'
import selectCurrentOffer from '../selectors/currentOffer'
import selectIsCurrentTuto from '../selectors/isCurrentTuto'
import selectIsFinished from '../selectors/isFinished'

const Clue = ({ distance, offer, isHidden, transitionTimeout, isCurrentTuto, isFinished }) => {
  return (
    <div
      className="clue"
      style={{ transition: `opacity ${transitionTimeout}ms` }}
    >
      <Finishable finished={isFinished && !isCurrentTuto // Hard coded to prevent a weird bug to arise, should be eventually removed
                           }>
        <Price value={offer && offer.price} />
        <div className="separator">{offer ? '\u00B7' : ' '}</div>
        <div>{offer ? distance : ' '}</div>
      </Finishable>
    </div>
  )
}

Clue.defaultProps = {
  transitionTimeout: 250,
}

export default connect(state => ({
  distance: selectDistance(state),
  isCurrentTuto: selectIsCurrentTuto(state),
  isFinished: selectIsFinished(state),
  isFlipped: state.verso.isFlipped,
  offer: selectCurrentOffer(state),
}))(Clue)
