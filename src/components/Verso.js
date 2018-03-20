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
      <h2>
        <div>{object.name}</div>
      </h2>
      <ControlBar {...props} />
      <OfferInfo {...userMediationOffers[0]} />
      <MediationCardBack {...mediation} />
    </div>
  )
}

export default Verso
