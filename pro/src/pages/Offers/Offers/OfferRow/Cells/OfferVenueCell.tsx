import React from 'react'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../OfferItem.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
}

export const OfferVenueCell = ({ venue }: OfferVenueCellProps) => {
  return (
    <td className={styles['venue-column']}>{computeVenueDisplayName(venue)}</td>
  )
}
