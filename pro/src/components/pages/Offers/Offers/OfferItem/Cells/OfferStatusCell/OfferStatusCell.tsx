import React from 'react'

import StatusLabel from 'components/pages/Offers/Offer/OfferStatus/StatusLabel'

import styles from '../../OfferItem.module.scss'

const OfferStatusCell = ({ status }: { status: string }) => (
  <td className={styles['status-column']}>
    <StatusLabel status={status} />
  </td>
)

export default OfferStatusCell
