import cn from 'classnames'

import type {
  CollectiveOfferBookableResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'

import styles from '../Cells.module.scss'

interface CollectiveOfferStatusCellProps {
  rowId: string
  offer:
    | CollectiveOfferTemplateResponseModel
    | CollectiveOfferBookableResponseModel
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
