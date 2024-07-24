import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'

import styles from '../OfferRow.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  headers?: string
}

export const OfferVenueCell = ({ venue, headers }: OfferVenueCellProps) => {
  return (
    <td className={styles['venue-column']} headers={headers}>
      {computeVenueDisplayName(venue)}
    </td>
  )
}
