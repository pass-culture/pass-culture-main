import PropTypes from 'prop-types'
import React from 'react'

import BookingOfferCellForEvent from './BookingOfferCellForEvent'
import BookingOfferCellForThing from './BookingOfferCellForThing'

const BookingOfferCell = ({ offer }) => {
  if (offer.event_beginning_datetime) {
    return (
      <BookingOfferCellForEvent
        eventDatetime={offer.event_beginning_datetime}
        offerId={offer.offer_identifier}
        offerName={offer.offer_name}
        venueDepartmentCode={offer.venue_department_code}
      />
    )
  }
  return (
    <BookingOfferCellForThing
      offerId={offer.offer_identifier}
      offerIsbn={offer.offer_isbn}
      offerName={offer.offer_name}
    />
  )
}

BookingOfferCell.defaultValues = {
  offer: {
    offer_isbn: null,
  },
}

BookingOfferCell.propTypes = {
  offer: PropTypes.shape({
    event_beginning_datetime: PropTypes.string,
    offer_isbn: PropTypes.string,
    offer_identifier: PropTypes.string,
    offer_name: PropTypes.string.isRequired,
    venue_department_code: PropTypes.string,
  }).isRequired,
}

export default BookingOfferCell
