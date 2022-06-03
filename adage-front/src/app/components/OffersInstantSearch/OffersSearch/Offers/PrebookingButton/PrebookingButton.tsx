import { format } from 'date-fns-tz'
import React, { useCallback, useState } from 'react'

import { OfferStockResponse } from 'api/gen'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from 'app/components/Layout/Notification/Notification'
import { useActiveFeature } from 'app/hooks/useActiveFeature'
import { Button } from 'app/ui-kit'
import { ReactComponent as HourGlassIcon } from 'assets/hourglass.svg'
import { preBookCollectiveStock, preBookStock } from 'repository/pcapi/pcapi'

import './PrebookingButton.scss'
import PrebookingModal from './PrebookingModal'
import { getErrorMessage } from './utils'

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
  const newCollectiveModel = useActiveFeature('ENABLE_NEW_COLLECTIVE_MODEL')

  const handleSearchButtonClick = () => {
    setIsModalOpen(true)
  }

  const closeModal = () => {
    setIsModalOpen(false)
  }

  const preBookCurrentStock = useCallback(async () => {
    const preBookRoute = newCollectiveModel
      ? preBookCollectiveStock
      : preBookStock
    return preBookRoute(stock.id)
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
  }, [newCollectiveModel, stock.id])

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
