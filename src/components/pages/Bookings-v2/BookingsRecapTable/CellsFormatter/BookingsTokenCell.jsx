import React from 'react'
import PropTypes from 'prop-types'

const BookingTokenCell = ({ bookingToken }) => (<span>
  {bookingToken || '-'}
</span>)

BookingTokenCell.defaultProps = {
  bookingToken: null,
}

BookingTokenCell.propTypes = {
  bookingToken: PropTypes.string,
}

export default BookingTokenCell
