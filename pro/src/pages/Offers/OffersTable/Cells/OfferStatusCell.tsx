import classNames from 'classnames'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel/StatusLabel'

import styles from './Cells.module.scss'

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
