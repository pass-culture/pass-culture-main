import React from 'react'

const BookingTokenCell = ({ bookingToken }) => {
  return (<span>
    {bookingToken || '-'}
  </span>)
}

export default BookingTokenCell
