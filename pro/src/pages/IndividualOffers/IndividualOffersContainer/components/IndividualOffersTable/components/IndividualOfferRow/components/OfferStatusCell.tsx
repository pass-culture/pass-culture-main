import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { CELLS_DEFINITIONS } from 'components/OffersTable/utils/cellDefinitions'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import styles from 'styles/components/Cells.module.scss'

interface OfferStatusCellProps {
  rowId: string
  status: OfferStatus
  displayLabel?: boolean
  className?: string
}

export const OfferStatusCell = ({ rowId, status, displayLabel, className }: OfferStatusCellProps) => (
  <td
    role="cell"
    className={classNames(
      styles['offers-table-cell'],
      styles['status-column'],
      className
    )}
    headers={`${rowId} ${CELLS_DEFINITIONS.STATUS.id}`}
  >
    {displayLabel &&
      <span
        className={styles['offers-table-cell-mobile-label']}
        aria-hidden={true}
      >
        {`${CELLS_DEFINITIONS.STATUS.title} :`}
      </span>}
    <StatusLabel status={status} />
  </td>
)
