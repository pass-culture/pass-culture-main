import format from 'date-fns/format'
import React, { useCallback, useState } from 'react'
import { getErrorMessage } from './utils'

import {
  NotificationType,
  Notification,
  NotificationComponent,
} from 'app/components/Layout/Notification/Notification'
import { ReactComponent as HourGlassIcon } from 'assets/hourglass.svg'
import { preBookStock } from 'repository/pcapi/pcapi'
import { StockType } from 'utils/types'

import './PrebookingButton.scss'

const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
}: {
  className?: string
  stock: StockType
  canPrebookOffers: boolean
}): JSX.Element => {
  const [hasPrebookedOffer, setHasPrebookedOffer] = useState(false)
  const [isButtonDisabled, setIsButtonDisabled] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)

  const preBookCurrentStock = useCallback(() => {
    setIsButtonDisabled(true)
    return preBookStock(stock.id)
      .then(() => {
        setHasPrebookedOffer(true)
        setNotification(
          new Notification(
            NotificationType.success,
            'Votre préréservation a été effectuée avec succès.'
          )
        )
      })
      .catch((error) =>
        setNotification(
          new Notification(
            NotificationType.error,
            getErrorMessage(error)
          )
        )
      )
  }, [stock.id])

  return (
    <>
      {canPrebookOffers && (
        <div className={`prebooking-button-container ${className}`}>
          {hasPrebookedOffer ? (
            <div className="prebooking-tag">
              <HourGlassIcon className="prebooking-tag-icon" />
              Pré-réservé
            </div>
          ) : (
            <>
              <button
                className="prebooking-button"
                disabled={isButtonDisabled}
                onClick={preBookCurrentStock}
                type="button"
              >
                Pré-réserver
              </button>
              {stock.bookingLimitDatetime && (
                <span className="prebooking-button-booking-limit">
                  avant le :{' '}
                  {format(new Date(stock.bookingLimitDatetime), 'dd/MM/yyyy')}
                </span>
              )}
            </>
          )}
        </div>
      )}
      {notification && <NotificationComponent notification={notification} />}
    </>
  )
}

export default PrebookingButton
