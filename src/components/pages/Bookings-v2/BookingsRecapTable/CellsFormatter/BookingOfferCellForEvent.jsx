import React from 'react'
import PropTypes from 'prop-types'
import moment from 'moment'
import { FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../utils/date'

const BookingOfferCellForEvent = ({ eventDatetime, offerName }) => {
  const eventDatetimeFormatted = moment(eventDatetime).format(FORMAT_DD_MM_YYYY_HH_mm)

  return (
    <span className="booking-offer-name">
      <p className="offer-name">
        {offerName}
      </p>
      <p className="event-date">
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
