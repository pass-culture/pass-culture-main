import React, { useState } from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import CancelCollectiveBookingModal from 'components/CancelCollectiveBookingModal'
import { BOOKING_STATUS } from 'core/Bookings/constants'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import { cancelCollectiveBookingAdapter } from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './CollectiveActionButtons.module.scss'

export interface CollectiveActionButtonsProps {
  bookingRecap: CollectiveBookingResponseModel
  reloadBookings: () => void
  isCancellable: boolean
}

export const CollectiveActionButtons = ({
  bookingRecap,
  reloadBookings,
  isCancellable,
}: CollectiveActionButtonsProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const notify = useNotification()
  const offerId = bookingRecap.stock.offerId
  const nonHumanizedOfferId = bookingRecap.stock.offerId
  const offerEditionUrl = useOfferEditionURL(true, nonHumanizedOfferId, false)

  const cancelBooking = async () => {
    const response = await cancelCollectiveBookingAdapter({ offerId })
    if (response.isOk) {
      notify.success(response.message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
      reloadBookings()
    } else {
      notify.error(response.message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }
  return (
    <>
      <div className={styles['action-buttons']}>
        {isCancellable && (
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
          <ButtonLink
            link={{ isExternal: false, to: offerEditionUrl }}
            variant={ButtonVariant.PRIMARY}
          >
            Modifier l’offre
          </ButtonLink>
        )}
      </div>
      {isModalOpen && (
        <CancelCollectiveBookingModal
          onDismiss={() => setIsModalOpen(false)}
          onValidate={cancelBooking}
        />
      )}
    </>
  )
}
