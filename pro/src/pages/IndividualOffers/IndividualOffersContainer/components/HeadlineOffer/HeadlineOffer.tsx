import { GET_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { Link } from 'react-router'
import useSWR from 'swr'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import {
  EngagementEvents,
  Events,
  INDIVIDUAL_OFFERS_NAVIGATION_SOURCE,
} from '@/commons/core/FirebaseEvents/constants'
import { WEBAPP_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import { api } from 'apiClient/api'
import { OfferStatus } from 'apiClient/v1'
import styles from './HeadlineOffer.module.scss'

export function HeadlineOffer() {
  const { logEvent } = useAnalytics()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const { headlineOffer } = useHeadlineOfferContext()

  const offerQuery = useSWR(
    headlineOffer?.id ? [GET_OFFER_QUERY_KEY, Number(headlineOffer?.id)] : null,
    ([, offerIdParam]) => api.getOffer({ path: { offer_id: offerIdParam } })
  )

  if (!headlineOffer || !offerQuery.data) {
    return
  }

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${headlineOffer.venueId}`
  const offerLink = getIndividualOfferUrl({
    offerId: offerQuery.data.id,
    mode:
      offerQuery.data.status === OfferStatus.DRAFT
        ? OFFER_WIZARD_MODE.CREATION
        : OFFER_WIZARD_MODE.READ_ONLY,
    step:
      offerQuery.data.status === OfferStatus.DRAFT || !isOfferExposureEnabled
        ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION
        : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE,
    isOfferExposureEnabled,
  })

  return (
    <div className={styles['headline-offer-container']}>
      <div className={styles['headline-offer-title-container']}>
        <h2 className={styles['headline-offer-title']}>Votre offre à la une</h2>
        <Button
          as="a"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          to={venuePreviewLink}
          opensInNewTab
          onClick={() => {
            logEvent(EngagementEvents.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
              offerId: headlineOffer.id,
              action: 'seeInApp',
            })
          }}
          label="Visualiser dans l’application"
        />
      </div>

      <Link
        className={styles['headline-offer-block']}
        to={offerLink}
        onClick={() => {
          logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
            used: INDIVIDUAL_OFFERS_NAVIGATION_SOURCE.HEADLINE_OFFER,
            offerId: offerQuery.data?.id,
          })
        }}
      >
        <Thumb
          className={styles['headline-offer-thumb']}
          url={headlineOffer.image?.url}
        />
        <p className={styles['headline-offer-name']}>{headlineOffer.name}</p>
      </Link>
    </div>
  )
}
