import React from 'react'

export interface BookingTokenCellProps {
  bookingToken?: string | null
}

const BookingTokenCell = ({ bookingToken }: BookingTokenCellProps) => (
  <span>{bookingToken || '-'}</span>
)

export default BookingTokenCell
