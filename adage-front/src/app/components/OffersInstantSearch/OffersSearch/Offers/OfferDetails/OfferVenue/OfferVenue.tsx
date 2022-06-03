import React from 'react'

import { OfferAddressType } from 'api/gen'
import { OfferType } from 'app/types/offers'

interface IOfferVenue {
  offerVenue?: {
    addressType: OfferAddressType
    otherAddress: string
    venueId: string
  }
  venue: OfferType['venue']
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
