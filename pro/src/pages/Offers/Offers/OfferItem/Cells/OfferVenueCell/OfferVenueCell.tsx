import React from 'react'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../../OfferItem.module.scss'

const OfferVenueCell = ({ venue }: { venue: ListOffersVenueResponseModel }) => {
  return (
    <td className={styles['venue-column']}>
      {venue && computeVenueDisplayName(venue)}
    </td>
  )
}

export default OfferVenueCell
