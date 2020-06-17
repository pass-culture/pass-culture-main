import React from 'react'
import PropTypes from 'prop-types'
import {
  computeStatusClassName,
  getBookingStatusDisplayInformationsOrDefault,
} from './utils/bookingStatusConverter'
import BookingStatusCellHistory from "./BookingStatusCellHistory"

const BookingStatusCell = ({ bookingRecapInfo }) => {
  let bookingStatus = bookingRecapInfo.original.booking_status
  const offerName = bookingRecapInfo.original.stock.offer_name
  bookingStatus = bookingStatus.toLowerCase()

  const bookingStatusDisplayInformations = getBookingStatusDisplayInformationsOrDefault(bookingStatus)
  const statusClassName = computeStatusClassName(bookingStatusDisplayInformations)
  const statusName = bookingStatusDisplayInformations.status
    ? bookingStatusDisplayInformations.status
    : bookingStatus
  const amount = bookingRecapInfo.original.booking_amount
    ? `Prix: ${bookingRecapInfo.original.booking_amount}€`
    : 'Prix: Gratuit'

  const bookedDate = bookingRecapInfo.original.booking_date
  const reimbursedDate = bookingRecapInfo.original.booking_recap_history.reimbursed_date
    ? bookingRecapInfo.original.booking_recap_history.reimbursed_date
    : null
  const cancellationDate = bookingRecapInfo.original.booking_recap_history.cancellation_date
    ? bookingRecapInfo.original.booking_recap_history.cancellation_date
    : null
  const validatedDate = bookingRecapInfo.original.booking_recap_history.date_used
    ? bookingRecapInfo.original.booking_recap_history.date_used
    : null

  return (
    <div className="booking-status-wrapper">
      <span className={`booking-status-label ${statusClassName}`}>
        {statusName}
      </span>
      <div className="bs-tooltip">
        <span className="bs-offer-title">
          {offerName}
        </span>
        <span className="bs-offer-amount">
          {amount}
        </span>
        <span className="bs-history-title">
          Historique
        </span>
        {bookedDate && <BookingStatusCellHistory historyDate={bookedDate} historyDateType='booking_date'/>}
        {cancellationDate && <BookingStatusCellHistory historyDate={cancellationDate} historyDateType='cancellation_date'/>}
        {validatedDate && <BookingStatusCellHistory historyDate={validatedDate} historyDateType='date_used'/>}
        {reimbursedDate && <BookingStatusCellHistory historyDate={reimbursedDate} historyDateType='payment_date'/>}
      </div>
    </div>
  )
}

BookingStatusCell.propTypes = {
  bookingRecapInfo: PropTypes.shape().isRequired,
}

export default BookingStatusCell
