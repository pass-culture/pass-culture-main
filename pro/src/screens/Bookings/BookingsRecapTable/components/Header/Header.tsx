import React from 'react'

import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import { Button } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'
import { pluralize } from 'utils/pluralize'

export interface HeaderProps {
  bookingsRecapFilteredLength: number
  isLoading: boolean
  queryBookingId?: string
  resetBookings: () => void
}

const Header = ({
  bookingsRecapFilteredLength,
  isLoading,
  queryBookingId,
  resetBookings,
}: HeaderProps) => {
  if (isLoading) {
    return (
      <div className="bookings-header-loading">
        Chargement des réservations...
      </div>
    )
  } else {
    return (
      <div className="bookings-header">
        {!queryBookingId ? (
          <span className="bookings-header-number">
            {pluralize(bookingsRecapFilteredLength, 'réservation')}
          </span>
        ) : (
          <Button
            variant={ButtonVariant.TERNARY}
            onClick={resetBookings}
            Icon={ResetIcon}
            iconPosition={IconPositionEnum.LEFT}
          >
            Voir toutes les réservations
          </Button>
        )}
      </div>
    )
  }
}

export default Header
