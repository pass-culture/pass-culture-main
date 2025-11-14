import { Link } from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import {
  type CollectiveOffer,
  isCollectiveOfferBookable,
} from '@/commons/core/OfferEducational/types'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { Tag } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './OfferNameCell.module.scss'

export interface OfferNameCellProps {
  offer: CollectiveOffer
}

export const OfferNameCell = ({ offer }: OfferNameCellProps) => {
  const isTemplateTable = !isCollectiveOfferBookable(offer)

  const offerId = computeURLCollectiveOfferId(offer.id, isTemplateTable)
  const draftOfferLink =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${offerId}/creation`

  const offerLink =
    draftOfferLink || `/offre/${offerId}/collectif/recapitulatif`

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
        <div className={styles['text-overflow-ellipsis']}>{offer.name}</div>
      </div>
    </Link>
  )
}
