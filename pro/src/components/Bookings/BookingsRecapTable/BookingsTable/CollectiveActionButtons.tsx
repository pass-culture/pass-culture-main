import { useState } from 'react'
import useSWR, { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { getErrorCode, isErrorAPIError } from 'apiClient/helpers'
import {
  CollectiveBookingResponseModel,
  CollectiveOfferAllowedAction,
} from 'apiClient/v1'
import {
  GET_BOOKINGS_QUERY_KEY,
  GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY,
  GET_COLLECTIVE_OFFER_QUERY_KEY,
} from 'commons/config/swrQueryKeys'
import { BOOKING_STATUS } from 'commons/core/Bookings/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { useOfferEditionURL } from 'commons/hooks/useOfferEditionURL'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { CancelCollectiveBookingModal } from 'components/CancelCollectiveBookingModal/CancelCollectiveBookingModal'
import { Button } from 'ui-kit/Button/Button'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveActionButtons.module.scss'

export interface CollectiveActionButtonsProps {
  bookingRecap: CollectiveBookingResponseModel
  isCancellable: boolean
}

export const CollectiveActionButtons = ({
  bookingRecap,
  isCancellable,
}: CollectiveActionButtonsProps) => {
  const { mutate } = useSWRConfig()
  const [isModalOpen, setIsModalOpen] = useState(false)
  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )

  const notify = useNotification()

  const offerId = bookingRecap.stock.offerId
  const offerEditionUrl = useOfferEditionURL({
    isOfferEducational: true,
    offerId,
    isShowcase: false,
  })

  const { data: offer } = useSWR(
    [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(bookingRecap.stock.offerId)],
    ([, offerIdParam]) => api.getCollectiveOffer(offerIdParam)
  )

  const bookingIsCancellable = areNewStatusesEnabled
    ? offer &&
      isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferAllowedAction.CAN_CANCEL
      )
    : isCancellable

  const cancelBooking = async () => {
    setIsModalOpen(false)
    if (!offerId) {
      notify.error('L’identifiant de l’offre n’est pas valide.')
      return
    }
    try {
      await api.cancelCollectiveOfferBooking(offerId)
      await mutate(
        (key) => Array.isArray(key) && key.includes(GET_BOOKINGS_QUERY_KEY)
      )
      await mutate([
        GET_COLLECTIVE_BOOKING_BY_ID_QUERY_KEY,
        Number(bookingRecap.bookingId),
      ])

      const cancelSucessNotification = areNewStatusesEnabled
        ? 'Vous avez annulé la réservation de cette offre. Elle n’est donc plus visible sur ADAGE.'
        : 'La réservation sur cette offre a été annulée avec succès, votre offre sera à nouveau visible sur ADAGE.'

      notify.success(cancelSucessNotification, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    } catch (error) {
      if (isErrorAPIError(error) && getErrorCode(error) === 'NO_BOOKING') {
        notify.error(
          'Cette offre n’a aucune reservation en cours. Il est possible que la réservation que vous tentiez d’annuler ait déjà été utilisée.'
        )
        return
      }
      notify.error(
        `Une erreur est survenue lors de l’annulation de la réservation.`,
        {
          duration: NOTIFICATION_LONG_SHOW_DURATION,
        }
      )
    }
  }

  return (
    <>
      <div className={styles['action-buttons']}>
        {bookingIsCancellable && (
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={() => setIsModalOpen(true)}
          >
            Annuler la{' '}
            {bookingRecap.bookingStatus === BOOKING_STATUS.PENDING
              ? 'préréservation'
              : 'réservation'}
          </Button>
        )}
        {bookingRecap.bookingStatus === BOOKING_STATUS.PENDING && (
          <ButtonLink to={offerEditionUrl} variant={ButtonVariant.PRIMARY}>
            Modifier l’offre
          </ButtonLink>
        )}
      </div>
      <CancelCollectiveBookingModal
        onDismiss={() => setIsModalOpen(false)}
        onValidate={cancelBooking}
        isDialogOpen={isModalOpen}
      />
    </>
  )
}
