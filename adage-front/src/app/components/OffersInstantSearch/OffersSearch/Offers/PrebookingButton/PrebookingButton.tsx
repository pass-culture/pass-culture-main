import React, { useCallback, useState } from 'react'

import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'app/components/Layout/Notification/Notification'
import { Button } from 'app/ui-kit'
import { ReactComponent as HourGlassIcon } from 'assets/hourglass.svg'
import { preBookStock } from 'repository/pcapi/pcapi'
import { getLocalDepartmentDatetimeFromPostalCode } from 'utils/date'
import { StockType, VenueType } from 'utils/types'

import './PrebookingButton.scss'

import PrebookingModal from './PrebookingModal'
import { getErrorMessage } from './utils'

const PrebookingButton = ({
  className,
  stock,
  canPrebookOffers,
  venue,
}: {
  className?: string
  stock: StockType
  canPrebookOffers: boolean
  venue: VenueType
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
              Pré-réservé
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
                  {getLocalDepartmentDatetimeFromPostalCode(
                    stock.bookingLimitDatetime,
                    venue.postalCode,
                    'dd/MM/yyyy'
                  )}
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
