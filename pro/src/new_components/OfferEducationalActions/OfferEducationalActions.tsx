import cn from 'classnames'
import React, { useState } from 'react'

import { Button } from 'ui-kit'

import { ReactComponent as IconActive } from './assets/icon-active.svg'
import { ReactComponent as IconInactive } from './assets/icon-inactive.svg'
import style from './OfferEducationalActions.module.scss'
import ConfirmModal from './OfferEducationalActionsModal'

interface IOfferEducationalActions {
  className?: string
  isOfferActive: boolean
  isBooked: boolean
  setIsOfferActive?(isActive: boolean): void
  resetActiveBookings?(): void
}

const OfferEducationalActions = ({
  className,
  isOfferActive,
  isBooked,
  resetActiveBookings,
  setIsOfferActive,
}: IOfferEducationalActions): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  return (
    <>
      {isModalOpen && resetActiveBookings && (
        <ConfirmModal
          onDismiss={() => setIsModalOpen(false)}
          onValidate={resetActiveBookings}
        />
      )}
      <div className={cn(style['actions'], className)}>
        {setIsOfferActive && (
          <Button
            Icon={isOfferActive ? IconInactive : IconActive}
            className={cn(style['actions-button'])}
            onClick={() => setIsOfferActive(!isOfferActive)}
            variant={Button.variant.TERNARY}
          >
            {isOfferActive ? 'Désactiver l’offre' : 'Activer l’offre'}
          </Button>
        )}

        {isBooked && resetActiveBookings && (
          <Button
            className={cn(style['actions-button'])}
            onClick={() => setIsModalOpen(true)}
            variant={Button.variant.SECONDARY}
          >
            Annuler la réservation
          </Button>
        )}
      </div>
    </>
  )
}

export default OfferEducationalActions
