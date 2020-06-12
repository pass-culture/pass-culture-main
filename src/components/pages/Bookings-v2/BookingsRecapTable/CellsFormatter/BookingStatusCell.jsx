import React from 'react'
import PropTypes from 'prop-types'
import {
  computeStatusClassName,
  getBookingStatusDisplayInformationsOrDefault,
} from './utils/bookingStatusConverter'

const BookingStatusCell = ({ bookingRecapInfo }) => {
  let bookingStatus = bookingRecapInfo.original.booking_status
  const offerName = bookingRecapInfo.original.stock.offer_name
  bookingStatus = bookingStatus.toLowerCase()

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(
    bookingStatus
  )
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)
  const statusName = bookingStatusDisplayInformations.status
    ? bookingStatusDisplayInformations.status
    : bookingStatus

  return (
    <div className="tooltip">
      <span className={`booking-status-label ${statusClassName}`}>
        {statusName}
      </span>
      <div className="history">
        <span className="bs-offer-title">
          {offerName}
        </span>
      </div>
    </div>
  )
}

BookingStatusCell.propTypes = {
  bookingRecapInfo: PropTypes.shape().isRequired,
}

export default BookingStatusCell
