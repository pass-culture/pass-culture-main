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
  return offer
    &&  (
          <div className='clue' style={{ transition: `opacity ${transitionTimeout}ms`}}>
            <Price value={offer.price} />
            <div className='separator'>&middot;</div>
            <div>
               {distance}
            </div>
          </div>
        )
    || []
}

Clue.defaultProps = {
  transitionTimeout: 250
}

export default connect(
  state => ({
    distance: selectDistance(state),
    isFlipped: state.navigation.isFlipped,
    offer: selectOffer(state),
    userMediation: selectUserMediation(state)
  }))(Clue)
