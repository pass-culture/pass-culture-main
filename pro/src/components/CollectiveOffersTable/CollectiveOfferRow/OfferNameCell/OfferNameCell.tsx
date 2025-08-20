import { Link } from 'react-router'

import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { Tag } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'
import styles from './OfferNameCell.module.scss'

export interface OfferNameCellProps {
  offer: CollectiveOfferResponseModel
  offerLink: string
}

export const OfferNameCell = ({ offer, offerLink }: OfferNameCellProps) => {
  return (
    <Link className={styles['title-column-with-thumb']} to={offerLink}>
      <div className={styles['title-column-thumb']}>
        <Thumb url={offer.imageUrl} />
      </div>
      <div>
        {offer.isShowcase && <Tag label="Offre vitrine" />}
        <div className={styles['title-column-name']}>{offer.name}</div>
      </div>
    </Link>
  )
}
