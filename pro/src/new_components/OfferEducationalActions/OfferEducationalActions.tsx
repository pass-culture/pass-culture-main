import cn from 'classnames'
import React, { useState } from 'react'

import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import CancelCollectiveBookingModal from '../CancelCollectiveBookingModal'

import { ReactComponent as IconActive } from './assets/icon-active.svg'
import { ReactComponent as IconInactive } from './assets/icon-inactive.svg'
import style from './OfferEducationalActions.module.scss'

interface IOfferEducationalActions {
  className?: string
  isOfferActive: boolean
  isBooked: boolean
  isCancellable: boolean
  setIsOfferActive?(isActive: boolean): void
  cancelActiveBookings?(): void
}

const OfferEducationalActions = ({
  className,
  isOfferActive,
  isBooked,
  isCancellable,
  cancelActiveBookings,
  setIsOfferActive,
}: IOfferEducationalActions): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      {isModalOpen && cancelActiveBookings && (
        <CancelCollectiveBookingModal
          onDismiss={() => setIsModalOpen(false)}
          onValidate={cancelActiveBookings}
        />
      )}
      <div className={cn(style['actions'], className)}>
        {!isBooked && setIsOfferActive && (
          <Button
            Icon={isOfferActive ? IconInactive : IconActive}
            className={style['actions-button']}
            onClick={() => setIsOfferActive(!isOfferActive)}
            variant={ButtonVariant.TERNARY}
          >
            {isOfferActive ? 'Désactiver l’offre' : 'Activer l’offre'}
          </Button>
        )}

        {isBooked && isCancellable && cancelActiveBookings && (
          <Button
            className={style['actions-button']}
            onClick={() => setIsModalOpen(true)}
            variant={ButtonVariant.SECONDARY}
          >
            Annuler la réservation
          </Button>
        )}
      </div>
    </>
  )
}

export default OfferEducationalActions
