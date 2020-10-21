import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { fetchFromApiWithCredentials } from 'utils/fetch'

const ActionsBar = props => {
  const {
    refreshOffers,
    selectedOfferIds,
    hideActionsBar,
    setSelectedOfferIds,
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
    trackDeactivateOffers(selectedOfferIds)
    handleClose()
  }
  function handleClose() {
    setSelectedOfferIds([])
    hideActionsBar()
  }
  function computeSelectedOffersLabel() {
    if (nbSelectedOffers > 1) {
      return `${nbSelectedOffers} offres sélectionnées`
    }
    return `${nbSelectedOffers} offre sélectionnée`
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
          className="primary-button"
          onClick={handleDeactivate}
          type="button"
        >
          <Icon svg="ico-status-inactive" />
          {'Désactiver'}
        </button>
        <button
          className="primary-button"
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
  trackActivateOffers: PropTypes.func.isRequired,
  trackDeactivateOffers: PropTypes.func.isRequired,
}

export default ActionsBar
