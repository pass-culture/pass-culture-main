import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import { OfferStockResponse } from 'apiClient/adageIframe'
import { apiAdage } from 'apiClient/api'
import './PrebookingButton.scss'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'pages/AdageIframe/app/components/Layout/Notification/Notification'
import { Button } from 'pages/AdageIframe/app/ui-kit'
import { ReactComponent as HourGlassIcon } from 'pages/AdageIframe/assets/hourglass.svg'
import { logOfferConversion } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { LOGS_DATA } from 'utils/config'

import { postBookingAdapater } from './adapters/postBookingAdapter'
import PrebookingModal from './PrebookingModal'

const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
  offerId,
  queryId,
}: {
  className?: string
  stock: OfferStockResponse
  canPrebookOffers: boolean
  offerId: number
  queryId: string
}): JSX.Element | null => {
  const [hasPrebookedOffer, setHasPrebookedOffer] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleBookingModalButtonClick = (stockId: number) => {
    if (LOGS_DATA) {
      apiAdage.logBookingModalButtonClick({ stockId })
    }
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  const preBookCurrentStock = useCallback(async () => {
    logOfferConversion(offerId.toString(), queryId)
    const { isOk, message } = await postBookingAdapater(stock.id)

    if (!isOk) {
      return setNotification(new Notification(NotificationType.error, message))
    }

    setHasPrebookedOffer(true)
    closeModal()
    setNotification(new Notification(NotificationType.success, message))
  }, [stock.id, offerId, queryId])

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
