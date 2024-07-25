import { CollectiveOfferResponseModel } from 'apiClient/v1'

import styles from './ExpirationCell.module.scss'

export type ExpirationCellProps = {
  offer: CollectiveOfferResponseModel
  headers?: string
}

export function ExpirationCell({ offer, headers }: ExpirationCellProps) {
  return (
    <td colSpan={8} headers={headers} className={styles['expiration-cell']}>
      <div className={styles['banner']}>Expire dans x jours {offer.id}</div>
    </td>
  )
}
