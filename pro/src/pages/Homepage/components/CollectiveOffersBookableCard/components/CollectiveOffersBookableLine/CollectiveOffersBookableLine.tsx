import { Link } from 'react-router'

import type { CollectiveOfferHomeResponseModel } from '@/apiClient/v1'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { formatDateTimeParts } from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import {
  COLLECTIVE_OFFER_STATUS_PROPERTIES,
  CollectiveStatusLabel,
} from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from '../../../CollectiveOffersLine.module.scss'
import { CollectiveOffersBookableCTA } from '../CollectiveOffersBookableCTA/CollectiveOffersBookableCTA'
import {
  CollectiveOffersBookableTag,
  getTagInfo,
} from '../CollectiveOffersBookableTag/CollectiveOffersBookableTag'

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
  const numberOfParticipants =
    collectiveStock.numberOfTickets + collectiveStock.numberOfTeachers
  return `Prévu le ${startDate} - ${numberOfParticipants} ${pluralizeFr(numberOfParticipants, 'participant', 'participants')}`
}

export const CollectiveOffersBookableLine = ({
  offer,
}: CollectiveOffersBookableLineProps): JSX.Element => {
  const offerId = computeURLCollectiveOfferId(offer.id)
  const offerLink = getCollectiveOfferLink(offerId, offer.displayedStatus)

  const dateAndTicketsCount = getDateAndTicketsCount(offer.collectiveStock)

  const tagLabel = offer.collectiveStock
    ? getTagInfo(offer.displayedStatus, offer.collectiveStock).label
    : ''

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Thumb
        className={styles['offer-line-thumb']}
        url={offer.imageUrl}
        alt={`Thumbnail for ${offer.name}`}
      />
      <div className={styles['offer-line-content']}>
        {offer.collectiveStock && (
          <CollectiveOffersBookableTag
            displayedStatus={offer.displayedStatus}
            stock={offer.collectiveStock}
          />
        )}
        <h4 className={styles['offer-line-content-primary']}>
          <Link
            className={styles['offer-line-link']}
            to={offerLink}
            aria-label={[
              tagLabel,
              offer.name,
              dateAndTicketsCount,
              COLLECTIVE_OFFER_STATUS_PROPERTIES[offer.displayedStatus].label,
            ]
              .filter(Boolean)
              .join(' - ')}
          >
            {offer.name}
          </Link>
        </h4>
        <div className={styles['offer-line-content-secondary']}>
          {dateAndTicketsCount}
        </div>
      </div>
      <div className={styles['offer-line-status']}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </div>
      <CollectiveOffersBookableCTA
        stock={offer.collectiveStock}
        displayedStatus={offer.displayedStatus}
        offerId={offer.id}
        offerLink={offerLink}
      />
    </div>
  )
}
