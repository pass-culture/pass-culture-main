import cn from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import { CELLS_DEFINITIONS } from 'components/OffersTable/utils/cellDefinitions'
import styles from 'styles/components/Cells.module.scss'

interface CollectiveOfferStatusCellProps {
  rowId: string
  offer: CollectiveOfferResponseModel
  className?: string
}

export const CollectiveOfferStatusCell = ({
  rowId,
  offer,
  className,
}: CollectiveOfferStatusCellProps) => (
  <td
    className={cn(styles['offers-table-cell'], styles['status-column'], className)}
    headers={`${rowId} ${CELLS_DEFINITIONS.STATUS.id}`}
  >
    <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
  </td>
)
