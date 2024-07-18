import React from 'react'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../OfferItem.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  offerId: number
}

export const OfferVenueCell = ({ venue, offerId }: OfferVenueCellProps) => {
  return (
    <td
      className={styles['venue-column']}
      headers={`collective-th-offer-${offerId} collective-th-venue`}
    >
      {computeVenueDisplayName(venue)}
    </td>
  )
}
