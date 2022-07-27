import PropTypes from 'prop-types'
import React from 'react'

import StatusLabel from 'components/pages/Offers/Offer/OfferStatus/StatusLabel'
import StatusToggleButton from 'components/pages/Offers/Offer/OfferStatus/StatusToggleButton'

export const OfferHeader = ({ offer, reloadOffer }) => (
  <div className="offer-header">
    <StatusToggleButton offer={offer} reloadOffer={reloadOffer} />
    <div className="separator" />
    <StatusLabel status={offer.status} />
  </div>
)

OfferHeader.propTypes = {
  offer: PropTypes.shape({
    id: PropTypes.string,
    isActive: PropTypes.bool,
    status: PropTypes.string,
  }).isRequired,
  reloadOffer: PropTypes.func.isRequired,
}
