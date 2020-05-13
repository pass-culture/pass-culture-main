import React from 'react'
import PropTypes from 'prop-types'
import moment from 'moment'

const BookingOfferCellForEvent = ({ offerName, eventDatetime }) => {
  let eventDatetimeUTC = moment(eventDatetime)
  let eventDatetimeDay = eventDatetimeUTC.format('DD/MM/YYYY')
  let eventDatetimeHour = eventDatetimeUTC.format('HH:mm')

  return (
    <span className="cell-offer">
      <p className="offer-name">
        {offerName}
      </p>
      <p className="event-date">
        {`${eventDatetimeDay} ${eventDatetimeHour}`}
      </p>
    </span>
  )
}

BookingOfferCellForEvent.propTypes = {
  eventDatetime: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForEvent
