import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

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
    toggleSelectAllCheckboxes,
    allOffersLength,
    areAllOffersSelected,
  } = props

  const nbSelectedOffers = selectedOfferIds.length

  const handleClose = useCallback(() => {
    setSelectedOfferIds([])
    hideActionsBar()
    toggleSelectAllCheckboxes()
  }, [hideActionsBar, setSelectedOfferIds])

  const handleActivate = useCallback(async () => {
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
  }, [
    selectedOfferIds,
    refreshOffers,
    showSuccessNotification,
    nbSelectedOffers,
    handleClose,
    trackActivateOffers,
  ])

  const handleDeactivate = useCallback(async () => {
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
  }, [
    selectedOfferIds,
    refreshOffers,
    showSuccessNotification,
    nbSelectedOffers,
    handleClose,
    trackDeactivateOffers,
  ])

  const computeSelectedOffersLabel = () => {
    if (areAllOffersSelected) {
      return allOffersLength > 1
        ? `${allOffersLength} offres sélectionnées`
        : `${allOffersLength} offre sélectionnée`
    }

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
