import React from 'react'

import { OfferFormStepper } from 'new_components/OfferFormStepper'

interface IOfferIndividualProps {
  children: JSX.Element
}

const OfferIndividual = ({ children }: IOfferIndividualProps): JSX.Element => {
  return (
    <div>
      <h1 style={{ color: 'blue' }}>screen: OfferIndividual</h1>

      <OfferFormStepper />

      <div>{children}</div>
    </div>
  )
}

export default OfferIndividual
