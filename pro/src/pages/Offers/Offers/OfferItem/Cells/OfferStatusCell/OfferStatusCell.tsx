import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { StatusLabel } from 'components/StatusLabel'

import styles from '../../OfferItem.module.scss'

const OfferStatusCell = ({ status }: { status: OfferStatus }) => (
  <td className={styles['status-column']}>
    <StatusLabel status={status} />
  </td>
)

export default OfferStatusCell
