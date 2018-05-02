import get from 'lodash.get'
import moment from 'moment'
import React from 'react'
import { connect } from 'react-redux'

import Price from './Price'
import Finishable from './layout/Finishable'
import selectDistance from '../selectors/distance'
import selectCurrentOffer from '../selectors/currentOffer'

const Clue = ({ distance, offer, isHidden, transitionTimeout }) => {
  const isFinished = moment(get(offer, 'bookingLimitDatetime')) < moment()
  return (
    <div
      className="clue"
      style={{ transition: `opacity ${transitionTimeout}ms` }}
    >
      <Finishable finished={isFinished}>
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
  isFlipped: state.verso.isFlipped,
  offer: selectCurrentOffer(state),
}))(Clue)
