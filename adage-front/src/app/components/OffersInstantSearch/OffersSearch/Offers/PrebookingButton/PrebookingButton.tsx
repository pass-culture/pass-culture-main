import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import { OfferStockResponse } from 'api/gen'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'app/components/Layout/Notification/Notification'
import { Button } from 'app/ui-kit'
import { ReactComponent as HourGlassIcon } from 'assets/hourglass.svg'
import './PrebookingButton.scss'
import { logBookingModalButton } from 'repository/pcapi/pcapi'

import { postBookingAdapater } from './adapters/postBookingAdapter'
import PrebookingModal from './PrebookingModal'

const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
}: {
  className?: string
  stock: OfferStockResponse
  canPrebookOffers: boolean
}): JSX.Element | null => {
  const [hasPrebookedOffer, setHasPrebookedOffer] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleBookingModalButtonClick = (stockId: number) => {
    logBookingModalButton(stockId)
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  const preBookCurrentStock = useCallback(async () => {
    const { isOk, message } = await postBookingAdapater(stock.id)

    if (!isOk) {
      return setNotification(new Notification(NotificationType.error, message))
    }

    setHasPrebookedOffer(true)
    closeModal()
    setNotification(
      new Notification(NotificationType.success, message as string)
    )
  }, [stock.id])

  return canPrebookOffers ? (
    <>
      <div className={`prebooking-button-container ${className}`}>
        {hasPrebookedOffer ? (
          <div className="prebooking-tag">
            <HourGlassIcon className="prebooking-tag-icon" />
            Préréservé
          </div>
        ) : (
          <>
            <Button
              className="prebooking-button"
              label="Préréserver"
              onClick={() => handleBookingModalButtonClick(stock.id)}
              type="button"
            />

            {stock.bookingLimitDatetime && (
              <span className="prebooking-button-booking-limit">
                avant le :{' '}
                {format(new Date(stock.bookingLimitDatetime), 'dd/MM/yyyy')}
              </span>
            )}
          </>
        )}
      </div>

      {notification && <NotificationComponent notification={notification} />}
      <PrebookingModal
        closeModal={closeModal}
        isOpen={isModalOpen}
        preBookCurrentStock={preBookCurrentStock}
      />
    </>
  ) : null
}

export default PrebookingButton
