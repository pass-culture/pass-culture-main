import classNames from 'classnames'

import { AddressResponseIsEditableModel } from 'apiClient/v1'
import { computeAddressDisplayName } from 'repository/venuesService'

import styles from './Cells.module.scss'

export function AddressCell({
  address,
}: {
  address: AddressResponseIsEditableModel
}) {
  return (
    <td
      className={classNames(
        styles['offers-table-cell'],
        styles['venue-column']
      )}
    >
      {computeAddressDisplayName(address)}
    </td>
  )
}
