import moment from 'moment/moment'
import React from 'react'

function BookingDateCell(props) {
  const { bookingDate } = props
  let bookingDateUTC = moment(bookingDate).utc()
  let bookingDateDay = bookingDateUTC.format('DD/MM/YYYY')
  let bookingDateHour = bookingDateUTC.format('HH:mm')
  return (
    <div>
      <span>
        {bookingDateDay}
      </span>
      <br />
      <span className="cell-subtitle">
        {bookingDateHour}
      </span>
    </div>
  )
}

export default BookingDateCell
