import React from 'react'

import { Venue } from 'core/Offers/types'
import { computeVenueDisplayName } from 'repository/venuesService'

const OfferVenueCell = ({ venue }: { venue: Venue }) => {
  return (
    <td className="venue-column">{venue && computeVenueDisplayName(venue)}</td>
  )
}

export default OfferVenueCell
