import React from 'react'
import PropTypes from 'prop-types'
import BookingOfferCellForThing from './BookingOfferCellForThing'
import BookingOfferCellForEvent from './BookingOfferCellForEvent'
import BookingOfferCellForBook from './BookingOfferCellForBook'

const BookingOfferCell = ({ offer }) => {
  let component
  if (offer.type === 'event') {
    component = (
      <BookingOfferCellForEvent
        eventDatetime={offer.event_beginning_datetime}
        offerName={offer.offer_name}
        venueDepartmentCode={offer.venue_department_code}
      />
    )
  } else {
    if (offer.type === 'book') {
      component = (
        <BookingOfferCellForBook
          offerIsbn={offer.offer_isbn}
          offerName={offer.offer_name}
        />
      )
    } else {
      component = <BookingOfferCellForThing offerName={offer.offer_name} />
    }
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
    offer_name: PropTypes.string.isRequired,
    type: PropTypes.string.isRequired,
  }).isRequired,
}

export default BookingOfferCell
