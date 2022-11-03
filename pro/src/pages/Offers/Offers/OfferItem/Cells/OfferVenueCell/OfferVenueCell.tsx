import React from 'react'

import { Venue } from 'core/Offers/types'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../../OfferItem.module.scss'

const OfferVenueCell = ({ venue }: { venue: Venue }) => {
  return (
    <td className={styles['venue-column']}>
      {venue && computeVenueDisplayName(venue)}
    </td>
  )
}

export default OfferVenueCell
