import PropTypes from 'prop-types'
import React from 'react'

const BookingOfferCellForThing = ({ offerId, offerIsbn, offerName }) => (
  <a
    href={`/offres/${offerId}/edition`}
    rel="noopener noreferrer"
    target="_blank"
    title={`${offerName} (ouverture dans un nouvel onglet)`}
  >
    <div className="booking-offer-name">
      {offerName}
    </div>
    {offerIsbn && (
      <div className="booking-offer-additional-info">
        {offerIsbn}
      </div>
    )}
  </a>
)

BookingOfferCellForThing.defaultProps = {
  offerIsbn: null,
}

BookingOfferCellForThing.propTypes = {
  offerId: PropTypes.string.isRequired,
  offerIsbn: PropTypes.string,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForThing
