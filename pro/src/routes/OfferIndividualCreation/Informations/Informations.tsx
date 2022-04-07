import React from 'react'

import { Informations as InformationsScreen } from 'screens/OfferIndividual/Informations'

const Informations = (): JSX.Element => {
  return (
    <div>
      <h2 style={{ color: 'red' }}>Route: Informations</h2>

      <InformationsScreen />
    </div>
  )
}

export default Informations
