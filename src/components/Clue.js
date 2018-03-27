import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import Price from './Price'
import currentUserMediation from '../selectors/currentUserMediation'
import currentOffer from '../selectors/currentOffer'

const Clue = ({
  currentOffer,
  isHidden,
  transitionTimeout
}) => {
  return (
    <div className={classnames('clue', { 'clue--hidden': isHidden })}
      style={{ transition: `opacity ${transitionTimeout}ms`}}>
      <div>
        <Price value={currentOffer.price} />
        <span className='clue__sep'>
          &middot;
        </span>
        <span>
          100m
        </span>
      </div>
    </div>
  )
}

Clue.defaultProps = {
  transitionTimeout: 250
}

export default connect(
  state => ({
    currentOffer: currentOffer(state),
    currentUserMediation: currentUserMediation(state),
    isFlipped: state.navigation.isFlipped
  }))(Clue)
