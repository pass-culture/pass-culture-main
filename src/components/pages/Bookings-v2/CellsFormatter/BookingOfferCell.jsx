import React from 'react'
import PropTypes from 'prop-types'

const BookingOfferCell = ({ offer: { offer_name: offerName } }) => (
  <span className="cell-offer-link">
    {offerName}
  </span>
)

BookingOfferCell.propTypes = {
  offer: PropTypes.shape({
    offer_name: PropTypes.string.isRequired,
  }).isRequired,
}

export default BookingOfferCell
