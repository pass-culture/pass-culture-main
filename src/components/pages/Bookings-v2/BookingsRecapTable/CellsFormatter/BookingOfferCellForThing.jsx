import React from 'react'
import PropTypes from 'prop-types'

const BookingOfferCellForThing = ({ offerName }) => (
  <span className="booking-offer-name">
    <p className="offer-name">
      {offerName}
    </p>
  </span>
)

BookingOfferCellForThing.propTypes = {
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForThing
