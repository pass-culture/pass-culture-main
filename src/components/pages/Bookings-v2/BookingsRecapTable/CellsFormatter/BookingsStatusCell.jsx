import React from 'react'
import PropTypes from 'prop-types'

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
]

const BOOKING_STATUS_DEFAULT = {
  id: 'default',
  className: 'default',
}

const getBookingStatusDisplayInformationsOrDefault = bookingStatusInfos => {
  const bookingStatusFound = BOOKING_STATUS.find(({ id }) => bookingStatusInfos === id)
  return bookingStatusFound ? bookingStatusFound : BOOKING_STATUS_DEFAULT
}

const computeStatusClassName = bookingStatusDisplayInformations => {
  return `bookings-status-${bookingStatusDisplayInformations.className}`
}

const BookingStatusCell = ({ bookingStatus }) => {
  bookingStatus = bookingStatus.toLowerCase()

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(
    bookingStatus
  )
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)
  const statusName = bookingStatusDisplayInformations.status
    ? bookingStatusDisplayInformations.status
    : bookingStatus

  return (<span className={`bookings-status-label ${statusClassName}`}>
    {statusName}
  </span>)
}

BookingStatusCell.propTypes = {
  bookingStatus: PropTypes.string.isRequired,
}

export default BookingStatusCell
