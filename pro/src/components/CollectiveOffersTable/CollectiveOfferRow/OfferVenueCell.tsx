import classNames from 'classnames'
import { computeVenueDisplayName } from 'repository/venuesService'

import type { ListOffersVenueResponseModel } from '@/apiClient/v1'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'

import styles from './Cells.module.scss'

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
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().STRUCTURE.id}`}
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
    </td>
  )
}
