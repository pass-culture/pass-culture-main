import * as pcapi from 'repository/pcapi/pcapi'

import {
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'
import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'

const StatusToggleButton = ({ offer, reloadOffer }) => {
  const notification = useNotification()
  const useSummaryPage = useActiveFeature('OFFER_FORM_SUMMARY_PAGE')

  const toggleOfferActiveStatus = useCallback(() => {
    pcapi
      .updateOffersActiveStatus([offer.id], !offer.isActive)
      .then(() => {
        reloadOffer()
        notification.success(
          `L’offre a bien été ${offer.isActive ? 'désactivée' : 'activée'}.`
        )
      })
      .catch(() => {
        notification.error(
          'Une erreur est survenue, veuillez réessayer ultérieurement.'
        )
      })
  }, [offer, reloadOffer])

  const activateAction = useSummaryPage ? 'Publier' : 'Activer'
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
          {activateAction}
        </>
      )}
    </button>
  )
}

StatusToggleButton.propTypes = {
  offer: PropTypes.shape({
    id: PropTypes.string,
    isActive: PropTypes.bool,
    status: PropTypes.string,
  }).isRequired,
  reloadOffer: PropTypes.func.isRequired,
}

export default StatusToggleButton
