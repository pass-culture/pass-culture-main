import PropTypes from 'prop-types'
import React from 'react'

const BookingOfferCellForThing = ({ offerId, offerName }) => (
  <a
    href={`/offres/${offerId}/edition`}
    rel="noopener noreferrer"
    target="_blank"
    title={`${offerName} (ouverture dans un nouvel onglet)`}
  >
    <div className="booking-offer-name">
      {offerName}
    </div>
  </a>
)

BookingOfferCellForThing.propTypes = {
  offerId: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForThing
