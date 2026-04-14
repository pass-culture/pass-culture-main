import { Link, useNavigate } from 'react-router'

import type { CollectiveOfferTemplateHomeResponseModel } from '@/apiClient/v1'
import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1/new'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { formatDateTimeParts } from '@/commons/utils/date'
import { CollectiveStatusLabel } from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
import { Button } from '@/design-system/Button/Button'
import { ButtonVariant } from '@/design-system/Button/types'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from '../../../CollectiveOffersLine.module.scss'

export type CollectiveOffersTemplateLineProps = {
  offer: CollectiveOfferTemplateHomeResponseModel
}

function formatOfferDates(
  dates: CollectiveOfferTemplateHomeResponseModel['dates']
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
  const navigate = useNavigate()
  const snackBar = useSnackBar()

  const formattedOfferDates = formatOfferDates(offer.dates)

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
          {formattedOfferDates}
        </div>
      </Link>
      <Link className={styles['offer-line-status']} to={offerLink}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </Link>
      {offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ? (
        <Button
          variant={ButtonVariant.SECONDARY}
          label="Créer une offre réservable"
          onClick={() => createOfferFromTemplate(navigate, snackBar, offer.id)}
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
