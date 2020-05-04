import React from 'react'
import classnames from 'classnames'

const BOOKING_STATUS_ENUM = [
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

function BookingStatusCell(props) {
  let { bookingStatus } = props
  bookingStatus = bookingStatus.toLowerCase()

  function computeStatusClassName(bookingStatusInfos) {
    const prefix = 'booking-status--'
    const [{ status }] = BOOKING_STATUS_ENUM.filter(({ value }) => bookingStatusInfos === value)
    return prefix + status
  }

  const statusClassName = computeStatusClassName(bookingStatus)

  return (
    <span className={classnames('booking-status-label', statusClassName)}>
      {bookingStatus}
    </span>
  )
}

export default BookingStatusCell
