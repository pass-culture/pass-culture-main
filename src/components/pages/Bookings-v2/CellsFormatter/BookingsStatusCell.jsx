import React from 'react'
import classnames from 'classnames'

const BOOKING_STATUS = [
  {
    value: 'validé',
    status: 'validated',
  },
  {
    value: 'annulé',
    status: 'cancelled',
  },
  {
    value: 'réservé',
    status: 'booked',
  },
]

const BookingStatusCell = ({ bookingStatus }) => {
  bookingStatus = bookingStatus.toLowerCase()

  const computeStatusClassName = bookingStatusInfos => {
    const prefix = 'bookings-status-'
    const [{ status }] = BOOKING_STATUS.filter(({ value }) => bookingStatusInfos === value)
    return prefix + status
  }

  const statusClassName = computeStatusClassName(bookingStatus)

  return (
    <span className={classnames('bookings-status-label', statusClassName)}>
      {bookingStatus}
    </span>
  )
}

export default BookingStatusCell
