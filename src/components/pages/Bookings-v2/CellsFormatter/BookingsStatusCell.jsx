import React from 'react'
import classnames from 'classnames'

const BOOKINGS_RECAP_STATUS_ENUM = [
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
  let { bookingStatusInfos } = props
  bookingStatusInfos = bookingStatusInfos.toLowerCase()

  function computeStatusClassName(bookingStatusInfos) {
    const prefix = 'booking-status--'
    const [{ status }] = BOOKINGS_RECAP_STATUS_ENUM.filter(
      ({ value }) => bookingStatusInfos === value
    )
    return prefix + status
  }

  const statusClassName = computeStatusClassName(bookingStatusInfos)

  return (
    <span className={classnames('booking-status-label', statusClassName)}>
      {bookingStatusInfos}
    </span>
  )
}

export default BookingStatusCell
