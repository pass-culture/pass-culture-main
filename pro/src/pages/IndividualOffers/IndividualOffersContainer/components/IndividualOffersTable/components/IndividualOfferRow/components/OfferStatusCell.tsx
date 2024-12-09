import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'
import styles from 'styles/components/Cells.module.scss'

interface OfferStatusCellProps {
  status: OfferStatus
}

export const OfferStatusCell = ({ status }: OfferStatusCellProps) => (
  <td
    role="cell"
    className={classNames(styles['offers-table-cell'], styles['status-column'])}
  >
    <StatusLabel status={status} />
  </td>
)
