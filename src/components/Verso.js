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
  const offer = userMediationOffers[0]
  const object = offer.thing || offer.eventOccurence.event
  return (
    <div className={classnames('verso absolute', {
      'verso--flipped': isFlipped
    })}>
      <OfferInfo {...userMediationOffers[0]}>
        <ControlBar {...props} />
      </OfferInfo>
      <MediationCardBack {...mediation} />
    </div>
  )
}

export default Verso
