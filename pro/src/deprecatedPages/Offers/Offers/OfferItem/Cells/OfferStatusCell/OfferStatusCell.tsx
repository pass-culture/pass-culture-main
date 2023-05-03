import React from 'react'

import { StatusLabel } from 'components/StatusLabel'

import styles from '../../OfferItem.module.scss'

const OfferStatusCell = () => (
  <td className={styles['status-column']}>
    <StatusLabel />
  </td>
)

export default OfferStatusCell
