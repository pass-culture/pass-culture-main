import React from 'react'
import PropTypes from 'prop-types'
import BookingOfferCellForThing from './BookingOfferCellForThing'
import BookingOfferCellForEvent from './BookingOfferCellForEvent'
import BookingOfferCellForBook from './BookingOfferCellForBook'

const BookingOfferCell = ({ offer }) => {
  switch (offer.type) {
    case 'event':
      return (
        <BookingOfferCellForEvent
          eventDatetime={offer.event_beginning_datetime}
          offerName={offer.offer_name}
          venueDepartmentCode={offer.venue_department_code}
        />
      )
    case 'book':
      return (<BookingOfferCellForBook
        offerIsbn={offer.offer_isbn}
        offerName={offer.offer_name}
              />)
    default:
      return <BookingOfferCellForThing offerName={offer.offer_name} />
  }
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
