import React from 'react'
import PropTypes from 'prop-types'
import {
  computeStatusClassName,
  getStatusIcon,
  getStatusName,
} from './utils/bookingStatusConverter'
import BookingStatusCellHistory from './BookingStatusCellHistory'
import Icon from '../../../../layout/Icon'

const BookingStatusCell = ({ bookingRecapInfo }) => {
  let bookingStatus = bookingRecapInfo.original.booking_status
  const offerName = bookingRecapInfo.original.stock.offer_name

  const statusClassName = computeStatusClassName(bookingStatus)
  const statusName = getStatusName(bookingStatus)
  const amount = computeBookingAmount(bookingRecapInfo.original.booking_amount)
  const icon = getStatusIcon(bookingStatus)

  function computeBookingAmount(amount) {
    const FREE_AMOUNT = 'Gratuit'
    const AMOUNT_SUFFIX = '\u00a0€'
    return amount ? `${amount}${AMOUNT_SUFFIX}` : FREE_AMOUNT
  }

  return (
    <div className="booking-status-wrapper">
      <span className={`booking-status-label ${statusClassName}`}>
        <Icon
          alt={`icone status ${statusName}`}
          svg={icon}
        />
        {statusName}
      </span>
      <div className="bs-tooltip">
        <div className="bs-offer-title">
          {offerName}
        </div>
        <div className="bs-offer-amount">
          {`Prix : ${amount.replace('.', ',')}`}
        </div>
        <div className="bs-history-title">
          {'Historique'}
        </div>
        <BookingStatusCellHistory
          bookingStatusHistory={bookingRecapInfo.original.booking_status_history}
        />
      </div>
    </div>
  )
}

BookingStatusCell.propTypes = {
  bookingRecapInfo: PropTypes.shape().isRequired,
}

export default BookingStatusCell
