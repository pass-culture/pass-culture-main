import moment from 'moment'
import PropTypes from 'prop-types'
import React from 'react'

import { FORMAT_DD_MM_YYYY, FORMAT_HH_mm } from '../../../../../utils/date'

const BookingDateCell = ({ bookingDate }) => {
  const bookingDateMoment = moment.parseZone(bookingDate)
  const bookingDateDay = bookingDateMoment.format(FORMAT_DD_MM_YYYY)
  const bookingDateHour = bookingDateMoment.format(FORMAT_HH_mm)

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
  bookingDate: PropTypes.string.isRequired,
}

export default BookingDateCell
