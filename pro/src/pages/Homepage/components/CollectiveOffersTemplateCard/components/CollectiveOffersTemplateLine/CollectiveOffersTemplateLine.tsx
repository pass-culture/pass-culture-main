import { Link } from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { formatDateTimeParts } from '@/commons/utils/date'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import type { CollectiveOffersVariantMap } from '@/pages/Homepage/components/types'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './CollectiveOffersTemplateLine.module.scss'

export type CollectiveOffersTemplateLineProps = {
  offer: CollectiveOffersVariantMap['TEMPLATE']
}

function getSecondaryContent(
  dates: CollectiveOffersVariantMap['TEMPLATE']['dates']
): string {
  if (!dates) {
    return ''
  }
  const { date: startDate } = formatDateTimeParts(dates.start)
  const { date: endDate } = formatDateTimeParts(dates.end)
  return `Du ${startDate} au ${endDate}`
}

export const CollectiveOffersTemplateLine = ({
  offer,
}: CollectiveOffersTemplateLineProps): JSX.Element => {
  const offerId = computeURLCollectiveOfferId(offer.id, true)
  const offerLink = getCollectiveOfferLink(offerId, offer.displayedStatus)

  const secondaryContent = getSecondaryContent(offer.dates)

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Link className={styles['offer-line-thumb']} to={offerLink}>
        <Thumb url={offer.imageUrl} alt={`Thumbnail for ${offer.name}`} />
        <span className={styles['visually-hidden']}>Voir l'offre</span>
      </Link>
      <Link className={styles['offer-line-content']} to={offerLink}>
        <Tag variant={TagVariant.DEFAULT} label="Offre vitrine" />
        <div className={styles['offer-line-content-primary']}>{offer.name}</div>
        <div className={styles['offer-line-content-secondary']}>
          {secondaryContent}
        </div>
      </Link>
      <Link className={styles['offer-line-status']} to={offerLink}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </Link>
      {offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ? (
        <Button
          variant={ButtonVariant.SECONDARY}
          label="Créer une offre réservable"
          as="a"
          to={`/offre/creation/collectif?templateId=${offer.id}`}
        />
      ) : (
        <Button
          variant={ButtonVariant.SECONDARY}
          label="Voir l'offre"
          as="a"
          to={offerLink}
        />
      )}
    </div>
  )
}
