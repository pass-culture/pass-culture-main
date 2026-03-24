import { useAnalytics } from '@/app/App/analytics/firebase'
import { useHeadlineOfferContext } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { EngagementEvents } from '@/commons/core/FirebaseEvents/constants'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'
import { WEBAPP_URL } from '@/commons/utils/config'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { Thumb } from '@/ui-kit/Thumb/Thumb'

import styles from './HeadlineOffer.module.scss'

export function HeadlineOffer() {
  const { logEvent } = useAnalytics()
  const selectedVenue = useAppSelector(ensureSelectedVenue)

  const { isHeadlineOfferAllowedForOfferer, headlineOffer } =
    useHeadlineOfferContext()

  if (!isHeadlineOfferAllowedForOfferer || !headlineOffer) {
    return
  }

  const venuePreviewLink = `${WEBAPP_URL}/lieu/${headlineOffer.venueId}`

  return (
    <div className={styles['headline-offer-container']}>
      <div className={styles['headline-offer-title-container']}>
        <h2 className={styles['headline-offer-title']}>Votre offre à la une</h2>
        <Button
          as="a"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          to={venuePreviewLink}
          isExternal
          opensInNewTab
          onClick={() => {
            logEvent(EngagementEvents.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER, {
              offerId: headlineOffer.id,
              action: 'seeInApp',
              venueId: selectedVenue.id,
            })
          }}
          label="Visualiser dans l’application"
        />
      </div>

      <div className={styles['headline-offer-block']}>
        <Thumb
          className={styles['headline-offer-thumb']}
          url={headlineOffer.image?.url}
        />
        <p className={styles['headline-offer-name']}>{headlineOffer.name}</p>
      </div>
    </div>
  )
}
