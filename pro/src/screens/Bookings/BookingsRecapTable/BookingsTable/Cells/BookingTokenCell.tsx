import React from 'react'

export interface BookingTokenCellProps {
  bookingToken?: string | null
}

export const BookingTokenCell = ({ bookingToken }: BookingTokenCellProps) => (
  <span>{bookingToken || '-'}</span>
)
