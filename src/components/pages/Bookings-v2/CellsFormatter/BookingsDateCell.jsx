import moment from 'moment/moment'
import React from 'react'

function BookingDateCell(values) {
  const {bookingDateInfo} = values.values
  let bookingDate = moment(bookingDateInfo).utc()
  let bookingDateDay = bookingDate.format('DD/MM/YYYY')
  let bookingDateHour = bookingDate.format('HH:mm')
  return (
    <div>
        <span>
          {bookingDateDay}
        </span>
      <br/>
      <span className={"cell-subtitle"}>
          {bookingDateHour}
        </span>
    </div>
  )
}

export default BookingDateCell
