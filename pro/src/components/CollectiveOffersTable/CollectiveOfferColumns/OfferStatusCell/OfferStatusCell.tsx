import type { CollectiveOffer } from '@/commons/core/OfferEducational/types'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'

import styles from './OfferStatusCell.module.scss'

interface CollectiveOfferStatusCellProps {
  offer: CollectiveOffer
}

export const OfferStatusCell = ({ offer }: CollectiveOfferStatusCellProps) => (
  <div className={styles['status-column']}>
    <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
  </div>
)
