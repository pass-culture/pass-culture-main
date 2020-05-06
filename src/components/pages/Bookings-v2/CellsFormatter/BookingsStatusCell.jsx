import React from 'react'
import classnames from 'classnames'

const BOOKING_STATUS = [
  {
    id: 'validated',
    status: 'validé',
    className: 'validated',
  },
  {
    id: 'cancelled',
    status: 'annulé',
    className: 'cancelled',
  },
  {
    id: 'booked',
    status: 'réservé',
    className: 'booked',
  },
  {
    id: 'reimbursed',
    status: 'remboursé',
    className: 'reimbursed',
  },
  {
    id: 'default',
    className: 'default',
  },
]

const STATUS_PREFIX = 'bookings-status-'

const BookingStatusCell = ({ bookingStatus }) => {
  bookingStatus = bookingStatus.toLowerCase()

  const getBookingStatusDisplayInformationsOrDefault = bookingStatusInfos => {
    const bookingStatusFound = BOOKING_STATUS.find(({ id }) => bookingStatusInfos === id)
    return bookingStatusFound
      ? bookingStatusFound
      : BOOKING_STATUS.find(({ id }) => id === 'default')
  }

  const computeStatusClassName = bookingStatusDisplayInformations => {
    return STATUS_PREFIX + bookingStatusDisplayInformations.className
  }

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(
    bookingStatus
  )
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)

  return (
    <span className={classnames('bookings-status-label', statusClassName)}>
      {bookingStatusDisplayInformations.status
        ? bookingStatusDisplayInformations.status
        : bookingStatus}
    </span>
  )
}

export default BookingStatusCell
