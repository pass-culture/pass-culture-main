import { Icon } from 'pass-culture-shared'
import React from 'react'

const NoBookingsMessage = () => {
  return (
    <div className="no-bookings">
      <Icon
        alt="Aucune réservation pour le moment"
        className="no-bookings-icon"
        svg="ico-no-bookings"
      />
      <p className="no-bookings-message">
        {'Aucune réservation pour le moment'}
      </p>
    </div>
  )
}

export default NoBookingsMessage
