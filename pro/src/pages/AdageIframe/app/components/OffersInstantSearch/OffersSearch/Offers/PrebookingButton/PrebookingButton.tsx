import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import { OfferStockResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import strokeHourglass from 'icons/stroke-hourglass.svg'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'pages/AdageIframe/app/components/Layout/Notification/Notification'
import './PrebookingButton.scss'
import { logOfferConversion } from 'pages/AdageIframe/libs/initAlgoliaAnalytics'
import { Button } from 'ui-kit'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

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
      apiAdage.logBookingModalButtonClick({
        AdageHeaderFrom: removeParamsFromUrl(location.pathname),
        stockId,
      })
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
    setNotification(
      new Notification(NotificationType.success, message as string)
    )
  }, [stock.id, offerId, queryId])

  return canPrebookOffers ? (
    <>
      <div className={`prebooking-button-container ${className}`}>
        {hasPrebookedOffer ? (
          <div className="prebooking-tag">
            <SvgIcon
              className="prebooking-tag-icon"
              src={strokeHourglass}
              alt=""
            />
            Préréservé
          </div>
        ) : (
          <>
            <Button
              className="prebooking-button"
              onClick={() => handleBookingModalButtonClick(stock.id)}
            >
              Préréserver
            </Button>

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
      {isModalOpen && (
        <PrebookingModal
          closeModal={closeModal}
          preBookCurrentStock={preBookCurrentStock}
        />
      )}
    </>
  ) : null
}

export default PrebookingButton
