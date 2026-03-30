import { Link } from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { formatDateTimeParts } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import type {
  CollectiveOffersCardVariant,
  CollectiveOffersVariantMap,
} from '../../../types'
import { CollectiveOffersBookableCTA } from '../CollectiveOffersBookableCTA/CollectiveOffersBookableCTA'
import { CollectiveOffersBookableTag } from '../CollectiveOffersBookableTag/CollectiveOffersBookableTag'
import styles from './CollectiveOffersBookableLine.module.scss'

type CollectiveOffersBookableLineProps = {
  offer: CollectiveOffersVariantMap[CollectiveOffersCardVariant.BOOKABLE]
}

export const CollectiveOffersBookableLine = ({
  offer,
}: CollectiveOffersBookableLineProps): JSX.Element => {
  const offerId = computeURLCollectiveOfferId(offer.id)
  const draftOfferLink =
    offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT &&
    `/offre/collectif/${offerId}/creation`

  const offerLink =
    draftOfferLink || `/offre/${offerId}/collectif/recapitulatif`

  let nameSubtitle = ''
  if (offer.collectiveStock) {
    const { date: startDate } = formatDateTimeParts(
      offer.collectiveStock.startDatetime
    )
    const numberOfTickets = offer.collectiveStock.numberOfTickets
    nameSubtitle = `Prévu le ${startDate} - ${numberOfTickets} ${pluralizeFr(numberOfTickets, 'participant', 'participants')}`
  }

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Link to={offerLink}>
        <Thumb url={offer.imageUrl} />
      </Link>
      <Link to={offerLink}>
        <div className={styles['offer-line-name']}>
          {offer.collectiveStock && (
            <CollectiveOffersBookableTag
              displayedStatus={offer.displayedStatus}
              stock={offer.collectiveStock}
            />
          )}
          <div className={styles['offer-line-name-title']}>{offer.name}</div>
          <div className={styles['offer-line-name-subtitle']}>
            {nameSubtitle}
          </div>
        </div>
      </Link>
      <Link to={offerLink}>
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
