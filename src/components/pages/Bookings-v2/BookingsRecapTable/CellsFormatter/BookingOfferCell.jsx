import React from 'react'
import PropTypes from 'prop-types'
import BookingOfferCellForThing from './BookingOfferCellForThing'
import BookingOfferCellForEvent from './BookingOfferCellForEvent'

const BookingOfferCell = ({ offer }) => {
  return offer.type === 'event' ? (
    <BookingOfferCellForEvent
      eventDatetime={offer.event_beginning_datetime}
      offerName={offer.offer_name}
    />
  ) : (
    <BookingOfferCellForThing offerName={offer.offer_name} />
  )
}

BookingOfferCell.propTypes = {
  offer: PropTypes.shape({
    type: PropTypes.string.isRequired,
    offer_name: PropTypes.string.isRequired,
  }).isRequired,
}

export default BookingOfferCell
