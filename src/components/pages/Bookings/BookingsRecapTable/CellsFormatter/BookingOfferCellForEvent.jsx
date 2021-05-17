import { format } from 'date-fns-tz'
import PropTypes from 'prop-types'
import React from 'react'

import { FORMAT_DD_MM_YYYY_HH_mm, toDateStrippedOfTimezone } from 'utils/date'

const BookingOfferCellForEvent = ({ eventDatetime, offerId, offerName }) => {
  const eventDatetimeFormatted = format(
    toDateStrippedOfTimezone(eventDatetime),
    FORMAT_DD_MM_YYYY_HH_mm
  )

  return (
    <a
      className="booking-offer-detail-link"
      href={`/offres/${offerId}/edition`}
      rel="noopener noreferrer"
      target="_blank"
      title={`${offerName} (ouverture dans un nouvel onglet)`}
    >
      <div className="booking-offer-name">
        {offerName}
      </div>
      <div className="booking-offer-additional-info">
        {eventDatetimeFormatted}
      </div>
    </a>
  )
}

BookingOfferCellForEvent.propTypes = {
  eventDatetime: PropTypes.string.isRequired,
  offerId: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForEvent
