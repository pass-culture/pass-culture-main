import moment from 'moment/moment'
import React from 'react'
import PropTypes from 'prop-types'

function BookingDateCell({ bookingDate }) {
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

BookingDateCell.propTypes = {
  bookingDate: PropTypes.string.isRequired,
}

export default BookingDateCell
