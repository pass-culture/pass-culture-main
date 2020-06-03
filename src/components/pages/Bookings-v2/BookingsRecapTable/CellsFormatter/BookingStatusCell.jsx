import React from 'react'
import PropTypes from 'prop-types'
import { computeStatusClassName, getBookingStatusDisplayInformationsOrDefault } from './utils/bookingStatusConverter'

const BookingStatusCell = ({ bookingStatus }) => {
  bookingStatus = bookingStatus.toLowerCase()

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(
    bookingStatus
  )
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)
  const statusName = bookingStatusDisplayInformations.status
    ? bookingStatusDisplayInformations.status
    : bookingStatus

  return (
    <span className={`booking-status-label ${statusClassName}`}>
      {statusName}
    </span>
  )
}

BookingStatusCell.propTypes = {
  bookingStatus: PropTypes.string.isRequired,
}

export default BookingStatusCell
