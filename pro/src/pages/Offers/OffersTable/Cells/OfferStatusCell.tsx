import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import styles from 'styles/components/Cells.module.scss'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'


interface OfferStatusCellProps {
  status: OfferStatus
}

export const OfferStatusCell = ({ status }: OfferStatusCellProps) => (
  <td
    className={classNames(styles['offers-table-cell'], styles['status-column'])}
  >
    <StatusLabel status={status} />
  </td>
)
