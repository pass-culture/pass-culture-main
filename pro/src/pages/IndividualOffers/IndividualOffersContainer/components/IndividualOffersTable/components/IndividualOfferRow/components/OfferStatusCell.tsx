import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import styles from 'styles/components/Cells.module.scss'

interface OfferStatusCellProps {
  status: OfferStatus
  displayLabel?: boolean
  className?: string
}

export const OfferStatusCell = ({ status, displayLabel, className }: OfferStatusCellProps) => (
  <td
    role="cell"
    className={classNames(
      styles['offers-table-cell'],
      styles['status-column'],
      className
    )}
  >
    {displayLabel &&
      <span
        className={styles['offers-table-cell-mobile-label']}
        aria-hidden={true}
      >
        Statut :
      </span>}
    <StatusLabel status={status} />
  </td>
)
