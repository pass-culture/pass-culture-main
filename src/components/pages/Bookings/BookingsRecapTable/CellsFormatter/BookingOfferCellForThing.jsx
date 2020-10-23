import PropTypes from 'prop-types'
import React from 'react'

const BookingOfferCellForThing = ({ offerName }) => (
  <span className="booking-offer-info">
    <p className="offer-name">
      {offerName}
    </p>
  </span>
)

BookingOfferCellForThing.propTypes = {
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForThing
