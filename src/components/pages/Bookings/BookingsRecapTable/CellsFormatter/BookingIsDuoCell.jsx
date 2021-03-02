import PropTypes from 'prop-types'
import React from 'react'

import { ReactComponent as DuoSvg } from 'icons/ico-duo.svg'

const BookingIsDuoCell = ({ isDuo }) => {
  return (
    <span className="bookings-duo-icon">
      {isDuo && <DuoSvg title="Réservation DUO" />}
    </span>
  )
}

BookingIsDuoCell.propTypes = {
  isDuo: PropTypes.bool.isRequired,
}

export default BookingIsDuoCell
