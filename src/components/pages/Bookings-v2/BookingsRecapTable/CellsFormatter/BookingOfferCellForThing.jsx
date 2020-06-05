import React from 'react'
import PropTypes from 'prop-types'

const BookingOfferCellForThing = ({ offerIsbn, offerName }) => (
  <span className="booking-offer-info">
    <p className="offer-name">
      {offerName}
    </p>
    <p className="offer-additional-info">
      {offerIsbn}
    </p>
  </span>
)

BookingOfferCellForThing.propTypes = {
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForThing
