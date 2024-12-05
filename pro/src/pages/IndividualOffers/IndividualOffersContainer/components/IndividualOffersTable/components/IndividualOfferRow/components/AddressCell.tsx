import classNames from 'classnames'

import { AddressResponseIsLinkedToVenueModel } from 'apiClient/v1'
import { computeAddressDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

export function AddressCell({
  address,
  displayLabel,
  className,
}: {
  address: AddressResponseIsLinkedToVenueModel | null | undefined
  displayLabel?: boolean
  className?: string
}) {
  return (
    <td
      role="cell"
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column'],
        className
      )}
    >
      {displayLabel && <span className={styles['offers-table-cell-mobile-label']}>Adresse :</span>}
      {address ? computeAddressDisplayName(address) : '-'}
    </td>
  )
}
