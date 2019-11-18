import PropTypes from 'prop-types'
import React from 'react'

import BookingItemContainer from './BookingItem/BookingItemContainer'

const BookingsList = ({ bookings, shouldDisplayToken }) => (
  <ul>
    {bookings.map(booking => (
      <BookingItemContainer
        booking={booking}
        key={booking.id}
        shouldDisplayToken={shouldDisplayToken}
      />
    ))}
  </ul>
)

BookingsList.defaultProps = {
  shouldDisplayToken: true,
}

BookingsList.propTypes = {
  bookings: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  shouldDisplayToken: PropTypes.bool,
}

export default BookingsList
