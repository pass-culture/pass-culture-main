import PropTypes from 'prop-types'
import React from 'react'

import OfferItemContainer from '../OfferItem/OfferItemContainer'

const OffersTableBody = ({ areAllOffersSelected, offers, selectOffer, selectedOfferIds }) => (
  <tbody className="offers-list">
    {offers.map(offer => (
      <OfferItemContainer
        disabled={areAllOffersSelected}
        isSelected={selectedOfferIds.includes(offer.id)}
        key={offer.id}
        offer={offer}
        selectOffer={selectOffer}
      />
    ))}
  </tbody>
)

OffersTableBody.propTypes = {
  areAllOffersSelected: PropTypes.bool.isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  selectOffer: PropTypes.func.isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string).isRequired,
}

export default OffersTableBody
