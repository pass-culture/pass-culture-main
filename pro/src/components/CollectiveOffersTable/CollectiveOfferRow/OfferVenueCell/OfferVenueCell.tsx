import { CollectiveOfferOfferVenue } from 'apiClient/adage'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { computeVenueDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

interface OfferVenueCellProps {
  venue: CollectiveOfferOfferVenue
  displayLabel?: boolean
}

export const OfferVenueCell = ({
  venue,
  displayLabel,
}: OfferVenueCellProps) => {
  return (
    <div>
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
