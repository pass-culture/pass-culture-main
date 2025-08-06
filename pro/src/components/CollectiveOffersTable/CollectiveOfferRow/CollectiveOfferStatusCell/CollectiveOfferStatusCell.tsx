import cn from 'classnames'
import styles from 'styles/components/Cells.module.scss'

import { CollectiveOfferResponseModel } from '@/apiClient//v1'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { getCellsDefinition } from '@/components/OffersTable/utils/cellDefinitions'

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
    role="cell"
    className={cn(
      styles['offers-table-cell'],
      styles['status-column'],
      className
    )}
    headers={`${rowId} ${getCellsDefinition().COLLECTIVE_STATUS.id}`}
  >
    <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
  </td>
)
