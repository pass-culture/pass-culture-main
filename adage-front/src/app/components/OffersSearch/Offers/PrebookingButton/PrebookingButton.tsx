import React, { useCallback, useState } from 'react'

import { NotificationType, Notification,
  NotificationComponent, } from 'app/components/Layout/Notification/Notification'
import { preBookStock } from 'repository/pcapi/pcapi'
import { StockType } from 'utils/types'
import './PrebookingButton.scss'

const PrebookingButton = ({className, stock, canPrebookOffers}: {className?: string, stock: StockType, canPrebookOffers: boolean}): JSX.Element => {
  const [isButtonDisabled, setIsButtonDisabled] = useState(false)
  const [notification, setNotification] = useState<Notification | null>(null)
  
  const preBookCurrentStock = useCallback(() => {
    setIsButtonDisabled(true)
    return preBookStock(stock.id)
      .then(() =>
        setNotification(
          new Notification(
            NotificationType.success,
            "Votre préréservation a été effectuée avec succès."
          )
        )
      )
      .catch(() =>
        setNotification(
          new Notification(
            NotificationType.error,
            "Impossible de préréserver cette offre.\nVeuillez contacter le support"
          )
        )
      )
  }, [stock.id])
  
  return (
    <>
      {canPrebookOffers && (
        <button
          className={`prebooking-button ${className}`}
          disabled={isButtonDisabled}
          onClick={preBookCurrentStock}
          type='button'
        >
          pré-réserver
        </button>
      )}
      {notification && <NotificationComponent notification={notification} />}
    </>
  )
}

export default PrebookingButton