import { useMemo } from 'react'
import { useSelector } from 'react-redux'
import { useNavigate } from 'react-router'

import { CollectiveBookingCancellationReasons, CollectiveOfferDisplayedStatus } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  Events,
  COLLECTIVE_OFFER_DUPLICATION_ENTRIES,
} from 'commons/core/FirebaseEvents/constants'
import { duplicateBookableOffer } from 'commons/core/OfferEducational/utils/duplicateBookableOffer'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import fullDuplicateIcon from 'icons/full-duplicate.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const CancelledBanner = ({ offerId, reason }: { offerId: number, reason?: CollectiveBookingCancellationReasons | null }) => {
  const { logEvent } = useAnalytics()
  const navigate = useNavigate()
  const selectedOffererId = useSelector(selectCurrentOffererId)
  const notify = useNotification()

  const message = useMemo(() => {
    switch (reason) {
      case CollectiveBookingCancellationReasons.REFUSED_BY_INSTITUTE:
      case CollectiveBookingCancellationReasons.REFUSED_BY_HEADMASTER:
        return "L’établissement scolaire a annulé la réservation."
      case CollectiveBookingCancellationReasons.EXPIRED:
      case undefined:
        return "La date d’évènement de votre offre est dépassée. Votre offre a automatiquement été annulée. Vous pouvez créer une nouvelle offre à partir de celle-ci."
      case CollectiveBookingCancellationReasons.OFFERER:
      case CollectiveBookingCancellationReasons.PUBLIC_API:
        return "Vous avez annulé l’offre. Vous pouvez la dupliquer si vous souhaitez la publier à nouveau."
      case CollectiveBookingCancellationReasons.BENEFICIARY:
      case CollectiveBookingCancellationReasons.FRAUD:
      case CollectiveBookingCancellationReasons.FRAUD_SUSPICION:
      case CollectiveBookingCancellationReasons.FRAUD_INAPPROPRIATE:
      case CollectiveBookingCancellationReasons.FINANCE_INCIDENT:
      case CollectiveBookingCancellationReasons.BACKOFFICE:
      case CollectiveBookingCancellationReasons.BACKOFFICE_EVENT_CANCELLED:
      case CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_MODIFIED:
      case CollectiveBookingCancellationReasons.BACKOFFICE_OFFER_WITH_WRONG_INFORMATION:
      case CollectiveBookingCancellationReasons.BACKOFFICE_OFFERER_BUSINESS_CLOSED:
      case CollectiveBookingCancellationReasons.OFFERER_CONNECT_AS:
      case CollectiveBookingCancellationReasons.OFFERER_CLOSED:
      case null:
        return "Le pass Culture a annulé votre offre. Vous avez été notifié par mail de la raison de votre annulation. Vous pouvez la dupliquer si vous souhaitez la publier à nouveau."
    }
  }, [reason])

  return (
    <Callout className={styles['callout']} variant={CalloutVariant.ERROR}>
      {message}
      <div className={styles['callout-margin']}>
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullDuplicateIcon}
          onClick={async () => {
            logEvent(Events.CLICKED_DUPLICATE_BOOKABLE_OFFER, {
              from: COLLECTIVE_OFFER_DUPLICATION_ENTRIES.OFFER_TIMELINE,
              offererId: selectedOffererId?.toString(),
              offerId,
              offerStatus: CollectiveOfferDisplayedStatus.CANCELLED,
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
