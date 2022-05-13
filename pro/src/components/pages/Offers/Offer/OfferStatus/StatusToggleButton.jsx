import * as pcapi from 'repository/pcapi/pcapi'

import {
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'

export const StatusToggleButton = ({
  notifyError,
  notifySuccess,
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
        notifySuccess(!offer.isActive)
      })
      .catch(() => {
        notifyError()
      })
  }, [offer, notifyError, notifySuccess, reloadOffer])

  return (
    <button
      className="tertiary-button with-icon"
      disabled={[OFFER_STATUS_PENDING, OFFER_STATUS_REJECTED].includes(
        offer.status
      )}
      onClick={toggleOfferActiveStatus}
      type="button"
    >
      {offer.status !== OFFER_STATUS_INACTIVE ? (
        <>
          <Icon svg="ico-status-inactive" />
          Désactiver
        </>
      ) : (
        <>
          <Icon svg="ico-status-validated" />
          Activer
        </>
      )}
    </button>
  )
}

StatusToggleButton.propTypes = {
  notifyError: PropTypes.func.isRequired,
  notifySuccess: PropTypes.func.isRequired,
  offer: PropTypes.shape({
    id: PropTypes.string,
    isActive: PropTypes.bool,
    status: PropTypes.string,
  }).isRequired,
  reloadOffer: PropTypes.func.isRequired,
}
