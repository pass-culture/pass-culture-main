import React from 'react'
import PropTypes from 'prop-types'
import Icon from 'components/layout/Icon'

const BookingIsDuoCell = ({ isDuo }) => {
  return (
    <span className="bookings-duo-icon">
      {isDuo && (
        <Icon
          alt="Réservation DUO"
          svg="ico-duo"
        />
      )}
    </span>
  )
}

BookingIsDuoCell.propTypes = {
  isDuo: PropTypes.bool.isRequired,
}

export default BookingIsDuoCell
