import React from 'react'

import { Venue as VenueScreen } from 'screens/OfferIndividual/Venue'

const Venue = (): JSX.Element => {
  return (
    <div>
      <h2 style={{ color: 'red' }}>Route: Venue</h2>

      <VenueScreen />
    </div>
  )
}

export default Venue
