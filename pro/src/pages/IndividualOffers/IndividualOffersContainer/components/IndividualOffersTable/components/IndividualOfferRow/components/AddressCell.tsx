import classNames from 'classnames'

import { AddressResponseIsLinkedToVenueModel } from 'apiClient/v1'
import { getCellsDefinition } from 'components/OffersTable/utils/cellDefinitions'
import { computeAddressDisplayName } from 'repository/venuesService'
import styles from 'styles/components/Cells.module.scss'

export function AddressCell({
  rowId,
  address,
  displayLabel,
  className,
}: {
  rowId: string
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
      headers={`${rowId} ${getCellsDefinition().ADDRESS.id}`}
    >
      {displayLabel && (
        <span
          className={styles['offers-table-cell-mobile-label']}
          aria-hidden={true}
        >
          {`${getCellsDefinition().ADDRESS.title} :`}
        </span>
      )}
      {address ? computeAddressDisplayName(address) : '-'}
    </td>
  )
}
