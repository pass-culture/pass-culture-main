import classNames from 'classnames'

import { AddressResponseIsNotLinkToVenueModel } from 'apiClient/v1'
import { computeAddressDisplayName } from 'repository/venuesService'

import styles from './Cells.module.scss'

export function AddressCell({
  address,
}: {
  address: AddressResponseIsNotLinkToVenueModel
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
