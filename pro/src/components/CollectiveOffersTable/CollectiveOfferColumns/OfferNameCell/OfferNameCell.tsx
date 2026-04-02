import { Link } from 'react-router'

import {
  type CollectiveOffer,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { Tag } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './OfferNameCell.module.scss'

export interface OfferNameCellProps {
  offer: CollectiveOffer
}

export const OfferNameCell = ({ offer }: OfferNameCellProps) => {
  const isTemplateTable = !isCollectiveOfferBookable(offer)

  const offerId = computeURLCollectiveOfferId(offer.id, isTemplateTable)
  const offerLink = getCollectiveOfferLink(offerId, offer.displayedStatus)

  return (
    <Link className={styles['title-column-with-thumb']} to={offerLink}>
      <div className={styles['title-column-thumb']}>
        <Thumb url={offer.imageUrl} size="small" />
      </div>
      <div className={styles['title-column-name']}>
        {isTemplateTable && <Tag label="Offre vitrine" />}
        {!isTemplateTable ? (
          <span
            className={styles['title-column-offer-id']}
          >{`N°${offer.id}`}</span>
        ) : null}
        <div>{offer.name}</div>
      </div>
    </Link>
  )
}
