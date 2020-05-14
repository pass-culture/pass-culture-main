import React from 'react'
import PropTypes from 'prop-types'
import { formatLocalTimeDateString } from '../../../../utils/timezone'

const BookingOfferCellForEvent = ({ offerName, eventDatetime, venueDepartmentCode }) => {
  const eventDatetimeFormatted = formatLocalTimeDateString(
    eventDatetime,
    venueDepartmentCode,
    'DD/MM/YYYY HH:mm'
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
