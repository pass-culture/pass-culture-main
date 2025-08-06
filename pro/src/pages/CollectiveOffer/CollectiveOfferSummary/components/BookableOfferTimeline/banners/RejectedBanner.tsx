import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'

import { CollectiveOfferDisplayedStatus } from '@/apiClient//v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import {
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
  Events,
} from '@/commons/core/FirebaseEvents/constants'
import { duplicateBookableOffer } from '@/commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useNotification } from '@/commons/hooks/useNotification'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import fullDuplicateIcon from '@/icons/full-duplicate.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const RejectedBanner = ({ offerId }: { offerId: number }) => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const notify = useNotification()

  return (
    <Callout className={styles['callout']} variant={CalloutVariant.ERROR}>
      Votre offre a été rejetée par notre équipe en charge du contrôle de
      conformité. Vous avez reçu un mail précisant les raisons de cette
      décision. Vous pouvez dupliquer cette offre et la corriger pour la publier
      et la soumettre à nouveau à notre équipe.
      <div className={styles['callout-margin']}>
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullDuplicateIcon}
          onClick={async () => {
            logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
              from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_TIMELINE,
              offererId: selectedOffererId?.toString(),
              offerId,
              offerStatus: CollectiveOfferDisplayedStatus.REJECTED,
              offerType: 'collective',
            })
            await duplicateBookableOffer(navigate, notify, offerId)
          }}
        >
          {"Dupliquer l'offre"}
        </Button>
      </div>
    </Callout>
  )
}
