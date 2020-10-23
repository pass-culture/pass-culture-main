import moment from 'moment'
import PropTypes from 'prop-types'
import React from 'react'

import { FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../utils/date'

const BookingOfferCellForEvent = ({ eventDatetime, offerName }) => {
  const eventDatetimeFormatted = moment.parseZone(eventDatetime).format(FORMAT_DD_MM_YYYY_HH_mm)

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
