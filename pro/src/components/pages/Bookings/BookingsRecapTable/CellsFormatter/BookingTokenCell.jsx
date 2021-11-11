/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import PropTypes from 'prop-types'
import React from 'react'

const BookingTokenCell = ({ bookingToken }) => (
  <span>
    {bookingToken || '-'}
  </span>
)

BookingTokenCell.defaultProps = {
  bookingToken: null,
}

BookingTokenCell.propTypes = {
  bookingToken: PropTypes.string,
}

export default BookingTokenCell
