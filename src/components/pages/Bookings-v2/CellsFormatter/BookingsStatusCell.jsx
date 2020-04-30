import React from 'react'

function BookingStatusCell(props) {
  const { bookingStatusInfos } = props

  function computeStatusClassName(bookingStatusInfos) {
    return bookingStatusInfos
  }

  const statusClassName = computeStatusClassName(bookingStatusInfos)

  return (<div className={statusClassName}>
    {bookingStatusInfos}
  </div>)
}

export default BookingStatusCell
