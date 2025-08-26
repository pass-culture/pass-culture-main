import cn from 'classnames'

import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import styles from '@/styles/components/Cells.module.scss'

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
    // biome-ignore lint/a11y: accepted for assistive tech
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
