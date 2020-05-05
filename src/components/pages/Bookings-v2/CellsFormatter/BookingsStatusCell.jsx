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
  {
    value: 'remboursé',
    status: 'reimbursed',
  },
]

const BookingStatusCell = ({ bookingStatus }) => {
  bookingStatus = bookingStatus.toLowerCase()

  const computeStatusClassName = bookingStatusInfos => {
    const prefix = 'bookings-status-'
    const bookingStatus = BOOKING_STATUS.find(({ value }) => bookingStatusInfos === value)
    const status = bookingStatus ? bookingStatus.status : 'default'
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
