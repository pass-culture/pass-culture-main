import React from 'react'

import { ADRESS_TYPE, OfferType } from 'app/types/offers'

interface IOfferVenue {
  offerVenue?: {
    addressType: ADRESS_TYPE
    otherAddress: string
    venueId: string
  }
  venue: OfferType['venue']
}

const OfferVenue = ({ offerVenue, venue }: IOfferVenue): JSX.Element => {
  if (offerVenue) {
    if (offerVenue.addressType === ADRESS_TYPE.OTHER) {
      return <div>{offerVenue.otherAddress}</div>
    } else if (offerVenue.addressType === ADRESS_TYPE.SCHOOL) {
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
