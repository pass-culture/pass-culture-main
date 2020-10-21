import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { fetchFromApiWithCredentials } from 'utils/fetch'

const computeActivationSuccessMessage = nbSelectedOffers => {
  const successMessage =
    nbSelectedOffers > 1 ? 'offres ont bien été activées' : 'offre a bien été activée'
  return `${nbSelectedOffers} ${successMessage}`
}
const computeDeactivationSuccessMessage = nbSelectedOffers => {
  const successMessage =
    nbSelectedOffers > 1 ? 'offres ont bien été désactivées' : 'offre a bien été désactivée'
  return `${nbSelectedOffers} ${successMessage}`
}

const ActionsBar = props => {
  const {
    refreshOffers,
    selectedOfferIds,
    hideActionsBar,
    setSelectedOfferIds,
    showSuccessNotification,
    trackActivateOffers,
    trackDeactivateOffers,
  } = props

  const nbSelectedOffers = selectedOfferIds.length

  async function handleActivate() {
    const body = {
      ids: selectedOfferIds,
      isActive: true,
    }

    await fetchFromApiWithCredentials('/offers/active-status', 'PATCH', body)
    refreshOffers({ shouldTriggerSpinner: false })
    showSuccessNotification(computeActivationSuccessMessage(nbSelectedOffers))
    handleClose()
    trackActivateOffers(selectedOfferIds)
    handleClose()
  }

  async function handleDeactivate() {
    const body = {
      ids: selectedOfferIds,
      isActive: false,
    }
    await fetchFromApiWithCredentials('/offers/active-status', 'PATCH', body)
    refreshOffers({ shouldTriggerSpinner: false })
    showSuccessNotification(computeDeactivationSuccessMessage(nbSelectedOffers))
    handleClose()
    trackDeactivateOffers(selectedOfferIds)
    handleClose()
  }

  function handleClose() {
    setSelectedOfferIds([])
    hideActionsBar()
  }

  function computeSelectedOffersLabel() {
    return nbSelectedOffers > 1
      ? `${nbSelectedOffers} offres sélectionnées`
      : `${nbSelectedOffers} offre sélectionnée`
  }

  return (
    <div
      className="offers-actions-bar"
      data-testid="offers-actions-bar"
    >
      <span className="nb-offers-description">
        {computeSelectedOffersLabel()}
      </span>

      <div className="actions-container">
        <button
          className="primary-button with-icon"
          onClick={handleDeactivate}
          type="button"
        >
          <Icon svg="ico-status-inactive" />
          {'Désactiver'}
        </button>
        <button
          className="primary-button with-icon"
          onClick={handleActivate}
          type="button"
        >
          <Icon svg="ico-status-validated" />
          {'Activer'}
        </button>
        <button
          className="button"
          onClick={handleClose}
          type="button"
        >
          {'Annuler'}
        </button>
      </div>
    </div>
  )
}

ActionsBar.defaultProps = {
  selectedOfferIds: [],
}

ActionsBar.propTypes = {
  hideActionsBar: PropTypes.func.isRequired,
  refreshOffers: PropTypes.func.isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string),
  setSelectedOfferIds: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  trackActivateOffers: PropTypes.func.isRequired,
  trackDeactivateOffers: PropTypes.func.isRequired,
}

export default ActionsBar
