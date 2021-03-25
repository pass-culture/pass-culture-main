import { format } from 'date-fns-tz'
import PropTypes from 'prop-types'
import React from 'react'

import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

const BookingOfferCellForEvent = ({ eventDatetime, offerName }) => {
  const eventDatetimeFormatted = format(
    toDateStrippedOfTimezone(eventDatetime),
    FORMAT_DD_MM_YYYY_HH_mm
  )

  return (
    <span className="booking-offer-info">
      <p className="offer-name">
        {offerName}
      </p>
      <p className="offer-additional-info">
        {eventDatetimeFormatted}
      </p>
    </span>
  )
}

BookingOfferCellForEvent.propTypes = {
  eventDatetime: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForEvent
