import { Link } from 'react-router'

import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { formatDateTimeParts } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from '../../../CollectiveOffersLine.module.scss'
import { CollectiveOffersBookableCTA } from '../CollectiveOffersBookableCTA/CollectiveOffersBookableCTA'
import { CollectiveOffersBookableTag } from '../CollectiveOffersBookableTag/CollectiveOffersBookableTag'

export type CollectiveOffersBookableLineProps = {
  offer: CollectiveOfferHomeResponseModel
}

function getDateAndTicketsCount(
  collectiveStock: CollectiveOfferHomeResponseModel['collectiveStock']
): string {
  if (!collectiveStock) {
    return ''
  }
  const { date: startDate } = formatDateTimeParts(collectiveStock.startDatetime)
  const numberOfTickets = collectiveStock.numberOfTickets
  return `Prévu le ${startDate} - ${numberOfTickets} ${pluralizeFr(numberOfTickets, 'participant', 'participants')}`
}

export const CollectiveOffersBookableLine = ({
  offer,
}: CollectiveOffersBookableLineProps): JSX.Element => {
  const offerId = computeURLCollectiveOfferId(offer.id)
  const offerLink = getCollectiveOfferLink(offerId, offer.displayedStatus)

  const dateAndTicketsCount = getDateAndTicketsCount(offer.collectiveStock)

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Link
        className={styles['offer-line-thumb']}
        to={offerLink}
        aria-label="Détail de l'offre"
      >
        <Thumb url={offer.imageUrl} alt={`Thumbnail for ${offer.name}`} />
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
          {dateAndTicketsCount}
        </div>
      </Link>
      <Link className={styles['offer-line-status']} to={offerLink}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </Link>
      <CollectiveOffersBookableCTA
        stock={offer.collectiveStock}
        displayedStatus={offer.displayedStatus}
        offerId={offer.id}
        offerLink={offerLink}
      />
    </div>
  )
}
