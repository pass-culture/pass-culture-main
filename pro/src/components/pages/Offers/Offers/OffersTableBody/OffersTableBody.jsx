import OfferItem from '../OfferItem/OfferItem'
import PropTypes from 'prop-types'
import React from 'react'

const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
  isNewModelEnabled,
  enableIndividualAndCollectiveSeparation
}) => (
  <tbody className="offers-list">
    {offers.map(offer => {
      let offerId = ''

      if (isNewModelEnabled) {
        offerId=`${offer.isShowcase ? `T-` : ''}${offer.id}`
      } else if (!isNewModelEnabled && enableIndividualAndCollectiveSeparation) {
        offerId = offer.offerId
      } else {
        offerId = offer.id
      }

      return (
        <OfferItem
          disabled={areAllOffersSelected}
          isSelected={selectedOfferIds.includes(offerId)}
          key={offerId}
          offer={offer}
          selectOffer={selectOffer}
          isNewModelEnabled={isNewModelEnabled}
          enableIndividualAndCollectiveSeparation={enableIndividualAndCollectiveSeparation}
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
  isNewModelEnabled: PropTypes.bool.isRequired,
  enableIndividualAndCollectiveSeparation: PropTypes.bool.isRequired
}

export default OffersTableBody
