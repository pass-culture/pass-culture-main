import classNames from 'classnames'

import { AddressResponseIsLinkedToVenueModel } from 'apiClient/v1'
import styles from 'styles/components/Cells.module.scss'
import { computeAddressDisplayName } from 'repository/venuesService'


export function AddressCell({
  address,
}: {
  address: AddressResponseIsLinkedToVenueModel | null | undefined
}) {
  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column']
      )}
    >
      {address ? computeAddressDisplayName(address) : '-'}
    </td>
  )
}
