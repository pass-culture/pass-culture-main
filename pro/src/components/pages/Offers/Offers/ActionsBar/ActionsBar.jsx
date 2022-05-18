import React, {useCallback, useState} from 'react'

import ConfirmDialog from "new_components/ConfirmDialog"
import { ReactComponent as EyeIcon } from 'icons/ico-eye-hidden.svg'
import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { updateOffersActiveStatus } from 'repository/pcapi/pcapi'

const computeActivationSuccessMessage = nbSelectedOffers => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été activées'
      : 'offre a bien été activée'
  return `${nbSelectedOffers} ${successMessage}`
}
const computeDeactivationSuccessMessage = nbSelectedOffers => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été désactivées'
      : 'offre a bien été désactivée'
  return `${nbSelectedOffers} ${successMessage}`
}

const computeAllActivationSuccessMessage = nbSelectedOffers =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours d’activation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours d’activation, veuillez rafraichir dans quelques instants'

const computeAllDeactivationSuccessMessage = nbSelectedOffers =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours de désactivation, veuillez rafraichir dans quelques instants'

const ActionsBar = props => {
  const {
    refreshOffers,
    selectedOfferIds,
    clearSelectedOfferIds,
    showPendingNotification,
    showSuccessNotification,
    toggleSelectAllCheckboxes,
    areAllOffersSelected,
    searchFilters,
    nbSelectedOffers,
  } = props

  const handleClose = useCallback(() => {
    clearSelectedOfferIds()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }, [clearSelectedOfferIds, areAllOffersSelected, toggleSelectAllCheckboxes])

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
      const body = areAllOffersSelected
        ? bodyAllActiveStatus
        : bodySomeActiveStatus

      updateOffersActiveStatus(areAllOffersSelected, body).then(() => {
        refreshOffers({ shouldTriggerSpinner: false })
        areAllOffersSelected
          ? showPendingNotification(
              isActivating
                ? computeAllActivationSuccessMessage(nbSelectedOffers)
                : computeAllDeactivationSuccessMessage(nbSelectedOffers)
            )
          : showSuccessNotification(
              isActivating
                ? computeActivationSuccessMessage(nbSelectedOffers)
                : computeDeactivationSuccessMessage(nbSelectedOffers)
            )
        handleClose()
      })
    },
    [
      searchFilters,
      selectedOfferIds,
      areAllOffersSelected,
      refreshOffers,
      showPendingNotification,
      nbSelectedOffers,
      showSuccessNotification,
      handleClose,
    ]
  )

  const handleActivate = useCallback(() => {
    handleUpdateOffersStatus(true)
  }, [handleUpdateOffersStatus])

  const handleDeactivate = useCallback(() => {
    handleUpdateOffersStatus(false)
    setIsConfirmDialogOpen(false)
  }, [handleUpdateOffersStatus])

  const computeSelectedOffersLabel = () => {
    if (nbSelectedOffers > 1) {
      return `${getOffersCountToDisplay(nbSelectedOffers)} offres sélectionnées`
    }

    return `${nbSelectedOffers} offre sélectionnée`
  }

  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)

  return (
    <div className="offers-actions-bar" data-testid="offers-actions-bar">
      <span>{computeSelectedOffersLabel()}</span>
      {
        isConfirmDialogOpen &&
        <ConfirmDialog
          cancelText={'Annuler'}
          confirmText={'Désactiver'}
          onCancel={()=>setIsConfirmDialogOpen(false)}
          onConfirm={handleDeactivate}
          icon={EyeIcon}
          title={ nbSelectedOffers === 1 ?
            `Vous avez sélectionné ${nbSelectedOffers} offre êtes-vous sur de vouloir la désactiver ?`
            : `Vous avez sélectionné ${nbSelectedOffers} offres êtes-vous sur de vouloir toutes les désactiver ?`}
        >
          {nbSelectedOffers === 1 ? "Dans ce cas elle ne sera plus visible sur l’application pass Culture par les jeunes." : "Dans ce cas elles ne seront plus visibles sur l’application pass Culture par les jeunes."}
        </ConfirmDialog>
      }
      <div className="actions-container">
        <button
          className="primary-button with-icon"
          onClick={()=>setIsConfirmDialogOpen(true)}
          type="button"
        >
          <Icon svg="ico-status-inactive" />
          Désactiver
        </button>
        <button
          className="primary-button with-icon"
          onClick={handleActivate}
          type="button"
        >
          <Icon svg="ico-status-validated" />
          Activer
        </button>
        <button
          className="secondary-button"
          onClick={handleClose}
          type="button"
        >
          Annuler
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
  clearSelectedOfferIds: PropTypes.func.isRequired,
  nbSelectedOffers: PropTypes.number.isRequired,
  refreshOffers: PropTypes.func.isRequired,
  searchFilters: PropTypes.shape().isRequired,
  selectedOfferIds: PropTypes.arrayOf(PropTypes.string),
  showPendingNotification: PropTypes.func.isRequired,
  showSuccessNotification: PropTypes.func.isRequired,
  toggleSelectAllCheckboxes: PropTypes.func.isRequired,
}

export default ActionsBar
