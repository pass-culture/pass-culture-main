import PropTypes from 'prop-types'
import React from 'react'

import BookingOfferCellForBook from './BookingOfferCellForBook'
import BookingOfferCellForEvent from './BookingOfferCellForEvent'
import BookingOfferCellForThing from './BookingOfferCellForThing'

const BookingOfferCell = ({ offer }) => {
  let component
  switch (offer.type) {
    case 'book':
      component = (
        <BookingOfferCellForBook
          offerIsbn={offer.offer_isbn}
          offerName={offer.offer_name}
        />
      )
      break
    case 'event':
      component = (
        <BookingOfferCellForEvent
          eventDatetime={offer.event_beginning_datetime}
          offerName={offer.offer_name}
          venueDepartmentCode={offer.venue_department_code}
        />
      )
      break
    default:
      component = <BookingOfferCellForThing offerName={offer.offer_name} />
  }

  return (
    <a
      className="booking-offer-detail-link"
      href={`/offres/${offer.offer_identifier}`}
    >
      {component}
    </a>
  )
}

BookingOfferCell.defaultValues = {
  offer: {
    offer_isbn: null,
  },
}

BookingOfferCell.propTypes = {
  offer: PropTypes.shape({
    offer_isbn: PropTypes.string,
    offer_identifier: PropTypes.string,
    offer_name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
    venue_department_code: PropTypes.string.isRequired,
  }).isRequired,
}

export default BookingOfferCell
