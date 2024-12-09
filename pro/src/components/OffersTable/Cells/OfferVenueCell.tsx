import classNames from 'classnames'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  headers?: string
}

export const OfferVenueCell = ({ venue, headers }: OfferVenueCellProps) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column']
      )}
      headers={headers}
    >
      {computeVenueDisplayName(venue)}
    </td>
  )
}
