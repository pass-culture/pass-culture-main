import React from 'react'
import PropTypes from 'prop-types'
import { formatLocalTimeDateString } from '../../../../../utils/timezone'

const FRENCH_FORMAT_DATETIME = 'DD/MM/YYYY HH:mm'
const BookingOfferCellForEvent = ({ offerName, eventDatetime, venueDepartmentCode }) => {
  const eventDatetimeFormatted = formatLocalTimeDateString(
    eventDatetime,
    venueDepartmentCode,
    FRENCH_FORMAT_DATETIME
  )
  return (
    <span className="cell-offer">
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
  venueDepartmentCode: PropTypes.string.isRequired,
}

export default BookingOfferCellForEvent
