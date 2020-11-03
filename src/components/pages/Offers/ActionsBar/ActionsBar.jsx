import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'

import { updateOffersActiveStatus } from '../../../../repository/pcapi/pcapi'

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
    areAllOffersSelected,
    searchFilters,
    nbSelectedOffers,
  } = props

  const handleClose = useCallback(() => {
    setSelectedOfferIds([])
    hideActionsBar()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }, [hideActionsBar, setSelectedOfferIds, areAllOffersSelected, toggleSelectAllCheckboxes])

  const handleUpdateOffersStatus = useCallback(
    isActivating => {
      const bodyAllActiveStatus = {
        ...searchFilters,
        isActive: isActivating,
      }
      const bodySomeActiveStatus = {
        ids: selectedOfferIds,
        isActive: isActivating,
      }
      const body = areAllOffersSelected ? bodyAllActiveStatus : bodySomeActiveStatus

      updateOffersActiveStatus(areAllOffersSelected, body).then(() => {
        refreshOffers({ shouldTriggerSpinner: false })
        showSuccessNotification(
          isActivating
            ? computeActivationSuccessMessage(nbSelectedOffers)
            : computeDeactivationSuccessMessage(nbSelectedOffers)
        )
        handleClose()
        if (!areAllOffersSelected) {
          isActivating
            ? trackActivateOffers(selectedOfferIds)
            : trackDeactivateOffers(selectedOfferIds)
        }
      })
    },
    [
      areAllOffersSelected,
      searchFilters,
      refreshOffers,
      showSuccessNotification,
      trackActivateOffers,
      trackDeactivateOffers,
      handleClose,
      nbSelectedOffers,
      selectedOfferIds,
    ]
  )

  const handleActivate = useCallback(() => {
    handleUpdateOffersStatus(true)
  }, [handleUpdateOffersStatus])

  const handleDeactivate = useCallback(() => {
    handleUpdateOffersStatus(false)
  }, [handleUpdateOffersStatus])

  const computeSelectedOffersLabel = () => {
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
  areAllOffersSelected: false,
  selectedOfferIds: [],
}

ActionsBar.propTypes = {
  areAllOffersSelected: PropTypes.bool,
  hideActionsBar: PropTypes.func.isRequired,
  refreshOffers: PropTypes.func.isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string),
  setSelectedOfferIds: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  toggleSelectAllCheckboxes: PropTypes.func.isRequired,
  trackActivateOffers: PropTypes.func.isRequired,
  trackDeactivateOffers: PropTypes.func.isRequired,
}

export default ActionsBar
