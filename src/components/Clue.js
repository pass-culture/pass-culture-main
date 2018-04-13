import React from 'react'
import { connect } from 'react-redux'

import Price from './Price'
import selectDistance from '../selectors/distance'
import selectOffer from '../selectors/offer'
import selectUserMediation from '../selectors/userMediation'

const Clue = ({
  distance,
  offer,
  isHidden,
  transitionTimeout
}) => {
  return (
    <div className='clue' style={{ transition: `opacity ${transitionTimeout}ms`}}>
      <Price value={offer && offer.price} />
      <div className='separator'>{ offer ? '\u00B7' : ' ' }</div>
      <div>
         { offer ? distance : ' ' }
      </div>
    </div>
  )
}

Clue.defaultProps = {
  transitionTimeout: 250
}

export default connect(
  state => ({
    distance: selectDistance(state),
    isFlipped: state.verso.isFlipped,
    offer: selectOffer(state),
    userMediation: selectUserMediation(state)
  }))(Clue)
