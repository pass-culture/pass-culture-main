import React, { useCallback } from 'react'

import Icon from 'components/layout/Icon'
import { TSearchFilters } from 'core/Offers/types'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { updateOffersActiveStatus } from 'repository/pcapi/pcapi'

const computeActivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été activées'
      : 'offre a bien été activée'
  return `${nbSelectedOffers} ${successMessage}`
}
const computeDeactivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été désactivées'
      : 'offre a bien été désactivée'
  return `${nbSelectedOffers} ${successMessage}`
}

const computeAllActivationSuccessMessage = (nbSelectedOffers: number) =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours d’activation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours d’activation, veuillez rafraichir dans quelques instants'

const computeAllDeactivationSuccessMessage = (nbSelectedOffers: number) =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours de désactivation, veuillez rafraichir dans quelques instants'

interface IActionBarProps {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  nbSelectedOffers: number
  refreshOffers: () => void
  searchFilters: TSearchFilters
  selectedOfferIds: string[]
  showPendingNotification: (message: string) => void
  showSuccessNotification: (message: string) => void
  toggleSelectAllCheckboxes: () => void
}

const ActionsBar = ({
  refreshOffers,
  selectedOfferIds,
  clearSelectedOfferIds,
  showPendingNotification,
  showSuccessNotification,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  searchFilters,
  nbSelectedOffers,
}: IActionBarProps): JSX.Element => {
  const handleClose = useCallback(() => {
    clearSelectedOfferIds()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }, [clearSelectedOfferIds, areAllOffersSelected, toggleSelectAllCheckboxes])

  const handleUpdateOffersStatus = useCallback(
    (isActivating: boolean) => {
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

      // @ts-expect-error Impossible d'assigner le type 'string' au type 'never'
      updateOffersActiveStatus(areAllOffersSelected, body).then(() => {
        refreshOffers()
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
  }, [handleUpdateOffersStatus])

  const computeSelectedOffersLabel = () => {
    if (nbSelectedOffers > 1) {
      return `${getOffersCountToDisplay(nbSelectedOffers)} offres sélectionnées`
    }

    return `${nbSelectedOffers} offre sélectionnée`
  }

  return (
    <div className="offers-actions-bar" data-testid="offers-actions-bar">
      <span>{computeSelectedOffersLabel()}</span>

      <div className="actions-container">
        <button
          className="primary-button with-icon"
          onClick={handleDeactivate}
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

export default ActionsBar
