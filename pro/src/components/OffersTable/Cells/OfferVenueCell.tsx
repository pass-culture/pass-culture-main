import classNames from 'classnames'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { computeVenueDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

interface OfferVenueCellProps {
  venue: ListOffersVenueResponseModel
  className?: string
  displayLabel?: boolean
}

export const OfferVenueCell = ({
  venue,
  className,
  displayLabel,
}: OfferVenueCellProps) => {
  const offerAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column'],
        className
      )}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {offerAddressEnabled ? 'Localisation :' : 'Lieu :'}
        </span>
      )}
      {computeVenueDisplayName(venue)}
    </td>
  )
}
