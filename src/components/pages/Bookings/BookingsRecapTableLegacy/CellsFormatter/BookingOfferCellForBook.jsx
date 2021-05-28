import PropTypes from 'prop-types'
import React from 'react'

const BookingOfferCellForBook = ({ offerId, offerIsbn, offerName }) => (
  <>
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
    <div className="booking-offer-additional-info">
      {offerIsbn}
    </div>
  </>
)

BookingOfferCellForBook.propTypes = {
  offerId: PropTypes.string.isRequired,
  offerIsbn: PropTypes.string.isRequired,
  offerName: PropTypes.string.isRequired,
}

export default BookingOfferCellForBook
