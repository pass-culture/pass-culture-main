import { Link } from 'react-router'

import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { formatDateTimeParts } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import type { CollectiveOffersVariantMap } from '../../../types'
import { CollectiveOffersBookableCTA } from '../CollectiveOffersBookableCTA/CollectiveOffersBookableCTA'
import { CollectiveOffersBookableTag } from '../CollectiveOffersBookableTag/CollectiveOffersBookableTag'
import styles from './CollectiveOffersBookableLine.module.scss'

export type CollectiveOffersBookableLineProps = {
  offer: CollectiveOffersVariantMap['BOOKABLE']
}

export const CollectiveOffersBookableLine = ({
  offer,
}: CollectiveOffersBookableLineProps): JSX.Element => {
  const offerId = computeURLCollectiveOfferId(offer.id)
  const offerLink = getCollectiveOfferLink(offerId, offer.displayedStatus)

  let secondaryContent = ''
  if (offer.collectiveStock) {
    const { date: startDate } = formatDateTimeParts(
      offer.collectiveStock.startDatetime
    )
    const numberOfTickets = offer.collectiveStock.numberOfTickets
    secondaryContent = `Prévu le ${startDate} - ${numberOfTickets} ${pluralizeFr(numberOfTickets, 'participant', 'participants')}`
  }

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Link className={styles['offer-line-thumb']} to={offerLink}>
        <Thumb url={offer.imageUrl} alt={`Thumbnail for ${offer.name}`} />
        <span className={styles['visually-hidden']}>Voir l'offre</span>
      </Link>
      <Link className={styles['offer-line-content']} to={offerLink}>
        {offer.collectiveStock && (
          <CollectiveOffersBookableTag
            displayedStatus={offer.displayedStatus}
            stock={offer.collectiveStock}
          />
        )}
        <div className={styles['offer-line-content-primary']}>{offer.name}</div>
        <div className={styles['offer-line-content-secondary']}>
          {secondaryContent}
        </div>
      </Link>
      <Link className={styles['offer-line-status']} to={offerLink}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </Link>
      <CollectiveOffersBookableCTA
        stock={offer.collectiveStock}
        offerId={offer.id}
        offerLink={offerLink}
      />
    </div>
  )
}
