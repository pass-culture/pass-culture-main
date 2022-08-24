import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'

const BookingIsDuoCell = ({ isDuo }: { isDuo: boolean }) => {
  return (
    <span className="bookings-duo-icon">
      {isDuo && <DuoSvg title="Réservation DUO" />}
    </span>
  )
}

export default BookingIsDuoCell
