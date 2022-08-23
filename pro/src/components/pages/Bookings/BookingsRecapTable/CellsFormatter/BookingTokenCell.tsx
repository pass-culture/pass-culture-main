import React from 'react'

const BookingTokenCell = ({
  bookingToken,
}: {
  bookingToken?: string | null
}) => <span>{bookingToken || '-'}</span>

export default BookingTokenCell
