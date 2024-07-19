import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../OfferRow.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
}

export const OfferVenueCell = ({ venue }: OfferVenueCellProps) => {
  return (
    <td className={styles['venue-column']}>{computeVenueDisplayName(venue)}</td>
  )
}
