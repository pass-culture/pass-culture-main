import { Link, useNavigate } from 'react-router'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferTemplateHomeResponseModel,
} from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { computeURLCollectiveOfferId } from '@/commons/core/OfferEducational/utils/computeURLCollectiveOfferId'
import { createOfferFromTemplate } from '@/commons/core/OfferEducational/utils/createOfferFromTemplate'
import { getCollectiveOfferLink } from '@/commons/core/OfferEducational/utils/getCollectiveOfferLink'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { formatDateTimeParts } from '@/commons/utils/date'
import {
  COLLECTIVE_OFFER_STATUS_PROPERTIES,
  CollectiveStatusLabel,
} from '@/components/CollectiveStatusLabel/CollectiveStatusLabel'
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
  const { logEvent } = useAnalytics()
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const formattedOfferDates = formatOfferDates(offer.dates)

  const onClickCreateBookableOffer = () => {
    logEvent(Events.CLICKED_DUPLICATE_TEMPLATE_OFFER, {
      offerId,
      offerType: 'collective',
      offerStatus: offer.displayedStatus,
    })
    createOfferFromTemplate(navigate, snackBar, offer.id, selectedPartnerVenue)
  }

  return (
    <div key={offer.id} className={styles['offer-line']}>
      <Thumb url={offer.imageUrl} alt={`Thumbnail for ${offer.name}`} />
      <div className={styles['offer-line-content']}>
        <Tag variant={TagVariant.DEFAULT} label="Offre vitrine" />
        <h3 className={styles['offer-line-content-primary']}>
          <Link
            className={styles['offer-line-link']}
            to={offerLink}
            aria-label={[
              'Offre vitrine',
              offer.name,
              formattedOfferDates,
              COLLECTIVE_OFFER_STATUS_PROPERTIES[offer.displayedStatus].label,
            ]
              .filter(Boolean)
              .join(' - ')}
          >
            {offer.name}
          </Link>
        </h3>
        <div className={styles['offer-line-content-secondary']}>
          {formattedOfferDates}
        </div>
      </div>
      <div className={styles['offer-line-status']}>
        <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      </div>
      {offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ? (
        <Button
          variant={ButtonVariant.SECONDARY}
          label="Créer une offre réservable"
          onClick={onClickCreateBookableOffer}
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
