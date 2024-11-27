import cn from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import styles from 'styles/components/Cells.module.scss'

interface CollectiveOfferStatusCellProps {
  offer: CollectiveOfferResponseModel
  headers?: string
}

export const CollectiveOfferStatusCell = ({
  offer,
  headers,
}: CollectiveOfferStatusCellProps) => (
  <td
    className={cn(styles['offers-table-cell'], styles['status-column'])}
    headers={headers}
  >
    <CollectiveStatusLabel
      offerDisplayedStatus={offer.displayedStatus}
    />
  </td>
)
