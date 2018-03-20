import classnames from 'classnames'
import React from 'react'

import ControlBar from './ControlBar'
import MediationCardBack from '../components/MediationCardBack'
import OfferInfo from '../components/OfferInfo'

const Verso = props => {
  const { deckElement,
    isFlipped,
    mediation,
    userMediationOffers
  } = props
  return (
    <div className={classnames('verso absolute', {
      'verso--flipped': isFlipped
    })}>
      <OfferInfo {...userMediationOffers[0]}>
        <ControlBar {...props} />
      </OfferInfo>
    </div>
  )
}

export default Verso
