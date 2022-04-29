import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'app/components/Layout/Notification/Notification'
import { StockType } from 'app/types/offers'
import { Button } from 'app/ui-kit'
import { ReactComponent as HourGlassIcon } from 'assets/hourglass.svg'
import { preBookStock } from 'repository/pcapi/pcapi'

import './PrebookingButton.scss'
import PrebookingModal from './PrebookingModal'
import { getErrorMessage } from './utils'

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
  const [notification, setNotification] = useState<Notification | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)

  const handleSearchButtonClick = () => {
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  const preBookCurrentStock = useCallback(async () => {
    return preBookStock(stock.id)
      .then(() => {
        setHasPrebookedOffer(true)
        closeModal()
        setNotification(
          new Notification(
            NotificationType.success,
            'Votre préréservation a été effectuée avec succès.'
          )
        )
      })
      .catch(error =>
        setNotification(
          new Notification(NotificationType.error, getErrorMessage(error))
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
              Préréservé
            </div>
          ) : (
            <>
              <Button
                className="prebooking-button"
                label="Préréserver"
                onClick={handleSearchButtonClick}
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
      )}
      {notification && <NotificationComponent notification={notification} />}
      <PrebookingModal
        closeModal={closeModal}
        isOpen={isModalOpen}
        preBookCurrentStock={preBookCurrentStock}
      />
    </>
  )
}

export default PrebookingButton
