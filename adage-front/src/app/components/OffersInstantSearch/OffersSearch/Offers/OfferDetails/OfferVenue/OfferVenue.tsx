import React from 'react'

import { OfferAddressType, OfferVenueResponse } from 'api/gen'

interface IOfferVenue {
  offerVenue?: {
    addressType: OfferAddressType
    otherAddress: string
    venueId: string
  }
  venue: OfferVenueResponse
}

const OfferVenue = ({ offerVenue, venue }: IOfferVenue): JSX.Element => {
  if (offerVenue) {
    if (offerVenue.addressType === OfferAddressType.Other) {
      return <div>{offerVenue.otherAddress}</div>
    } else if (offerVenue.addressType === OfferAddressType.School) {
      return <div>Dans l’établissement scolaire</div>
    }
  }

  return (
    <div>
      <div>{venue.name ?? venue.publicName}</div>
      <div>
        {venue.address}, {venue.postalCode} {venue.city}
      </div>
    </div>
  )
}

export default OfferVenue
