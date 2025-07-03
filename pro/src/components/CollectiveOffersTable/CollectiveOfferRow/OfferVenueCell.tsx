import classNames from 'classnames'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { computeVenueDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  rowId: string
  className?: string
  displayLabel?: boolean
}

export const OfferVenueCell = ({
  venue,
  rowId,
  className,
  displayLabel,
}: OfferVenueCellProps) => {
  return (
    <div
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column'],
        className
      )}
      //headers={`${rowId} ${getCellsDefinition().VENUE.id}`}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {`${getCellsDefinition().VENUE.title} :`}
        </span>
      )}
      {computeVenueDisplayName(venue)}
    </div>
  )
}
