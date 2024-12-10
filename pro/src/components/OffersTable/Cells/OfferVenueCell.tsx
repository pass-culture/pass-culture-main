import classNames from 'classnames'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { computeVenueDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  headers?: string
  className?: string
  displayLabel?: boolean
}

export const OfferVenueCell = ({ venue, headers, className, displayLabel }: OfferVenueCellProps) => {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column'],
        className
      )}
      headers={headers}
    >
      {displayLabel &&
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          Lieu :
        </span>}
      {computeVenueDisplayName(venue)}
    </td>
  )
}
