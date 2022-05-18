import OfferItem from '../OfferItem/OfferItem'
import PropTypes from 'prop-types'
import React from 'react'

const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
  isNewModelEnabled,
}) => (
  <tbody className="offers-list">
    {offers.map(offer => {
      const offerId = isNewModelEnabled ? `${offer.isShowcase ? `T-` : ''}${offer.id}` : offer.id
      return (
        <OfferItem
          disabled={areAllOffersSelected}
          isSelected={selectedOfferIds.includes(offerId)}
          key={offerId}
          offer={offer}
          selectOffer={selectOffer}
        />
      )
    })}
  </tbody>
)

OffersTableBody.propTypes = {
  areAllOffersSelected: PropTypes.bool.isRequired,
  offers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  selectOffer: PropTypes.func.isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string).isRequired,
  isNewModelEnabled: PropTypes.bool.isRequired
}

export default OffersTableBody
