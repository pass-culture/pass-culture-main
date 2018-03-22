import classnames from 'classnames'
import React from 'react'

import ControlBar from './ControlBar'
import MediationCardBack from '../components/MediationCardBack'
import OfferInfo from '../components/OfferInfo'

const Verso = props => {
  const {
    deckElement,
    isFlipped,
    mediation,
    chosenOffer,
  } = props
  return (
    <div className={classnames('verso absolute', {
      'verso--flipped': isFlipped
    })}>
      <OfferInfo {...chosenOffer}>
        <ControlBar {...props} />
      </OfferInfo>
      <MediationCardBack {...mediation} />
    </div>
  )
}

export default Verso
