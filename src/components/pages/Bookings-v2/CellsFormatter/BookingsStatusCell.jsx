import React from 'react'
import classnames from 'classnames'

function BookingStatusCell(props) {
  let { bookingStatusInfos } = props
  bookingStatusInfos = bookingStatusInfos.toLowerCase()

  function computeStatusClassName(bookingStatusInfos) {
    const prefix = 'booking-status--'
    let status = 'reserve'
    if (bookingStatusInfos === 'validé') status = 'valide'
    if (bookingStatusInfos === 'annulé') status = 'annule'
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
