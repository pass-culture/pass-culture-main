import format from 'date-fns/format'
import React, { useCallback, useState } from 'react'

import {
  NotificationType,
  Notification,
  NotificationComponent,
} from 'app/components/Layout/Notification/Notification'
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
  const [isButtonDisabled, setIsButtonDisabled] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)

  const preBookCurrentStock = useCallback(() => {
    setIsButtonDisabled(true)
    return preBookStock(stock.id)
      .then(() =>
        setNotification(
          new Notification(
            NotificationType.success,
            'Votre préréservation a été effectuée avec succès.'
          )
        )
      )
      .catch(() =>
        setNotification(
          new Notification(
            NotificationType.error,
            'Impossible de préréserver cette offre.\nVeuillez contacter le support'
          )
        )
      )
  }, [stock.id])

  return (
    <>
      {canPrebookOffers && (
        <div className={`prebooking-button-container ${className}`}>
          <button
            className="prebooking-button"
            disabled={isButtonDisabled}
            onClick={preBookCurrentStock}
            type="button"
          >
            pré-réserver
          </button>
          {stock.bookingLimitDatetime && (
            <span>
              avant le :{' '}
              {format(new Date(stock.bookingLimitDatetime), 'dd/MM/yyyy')}
            </span>
          )}
        </div>
      )}
      {notification && <NotificationComponent notification={notification} />}
    </>
  )
}

export default PrebookingButton
