import format from 'date-fns/format'
import PropTypes from 'prop-types'
import React from 'react'

import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

const BookingDateCell = ({ bookingDateIsoString }) => {
  const bookingDate = toDateStrippedOfTimezone(bookingDateIsoString)
  const bookingDateDay = format(bookingDate, FORMAT_DD_MM_YYYY)
  const bookingDateHour = format(bookingDate, FORMAT_HH_mm)

  return (
    <div>
      <span>
        {bookingDateDay}
      </span>
      <br />
      <span className="booking-date-subtitle">
        {bookingDateHour}
      </span>
    </div>
  )
}

BookingDateCell.propTypes = {
  bookingDateIsoString: PropTypes.string.isRequired,
}

export default BookingDateCell
