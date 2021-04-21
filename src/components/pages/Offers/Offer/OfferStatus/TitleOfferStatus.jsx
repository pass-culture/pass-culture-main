import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import OfferStatus from 'components/pages/Offers/Offer/OfferStatus/OfferStatus'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'components/pages/Offers/Offers/_constants'
import * as pcapi from 'repository/pcapi/pcapi'

export const TitleOfferStatus = ({
  notifySuccessfulOfferActivationStatusToggle,
  offer,
  reloadOffer,
}) => {
  const toggleOfferActiveStatus = useCallback(() => {
    pcapi
      .updateOffersActiveStatus(false, {
        ids: [offer.id],
        isActive: !offer.isActive,
      })
      .then(() => {
        reloadOffer()
        notifySuccessfulOfferActivationStatusToggle(!offer.isActive)
      })
  }, [offer, notifySuccessfulOfferActivationStatusToggle, reloadOffer])

  return (
    <>
      <button
        disabled={offer.status === OFFER_STATUS_PENDING || offer.status === OFFER_STATUS_REJECTED}
        onClick={toggleOfferActiveStatus}
        type="button"
      >
        {offer.isActive ? "Désactiver l'offre" : "Activer l'offre"}
      </button>
      <OfferStatus status={offer.status} />
    </>
  )
}

TitleOfferStatus.propTypes = {
  notifySuccessfulOfferActivationStatusToggle: PropTypes.func.isRequired,
  offer: PropTypes.shape({
    id: PropTypes.string,
    isActive: PropTypes.bool,
    status: PropTypes.string,
  }).isRequired,
  reloadOffer: PropTypes.func.isRequired,
}
