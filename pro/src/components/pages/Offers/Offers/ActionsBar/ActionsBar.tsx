import React, { useCallback, useState } from 'react'

import { Audience } from 'core/shared'
import ConfirmDialog from 'new_components/ConfirmDialog'
import { Events } from 'core/FirebaseEvents/constants'
import { ReactComponent as EyeIcon } from 'icons/ico-eye-hidden.svg'
import Icon from 'components/layout/Icon'
import { NBSP } from '../../Offer/Thumbnail/_constants'
import { RootState } from 'store/reducers'
import { TSearchFilters } from 'core/Offers/types'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { searchFiltersSelector } from 'store/offers/selectors'
import { updateAllCollectiveOffersActiveStatusAdapter } from './adapters/updateAllCollectiveOffersActiveStatusAdapter'
import { updateAllOffersActiveStatusAdapter } from './adapters/updateAllOffersActiveStatusAdapter'
import { updateCollectiveOffersActiveStatusAdapter } from './adapters/updateCollectiveOffersActiveStatusAdapter'
import { updateOffersActiveStatusAdapter } from './adapters/updateOffersActiveStatusAdapter'
import { useLocation } from 'react-router-dom'
import useNotification from 'components/hooks/useNotification'
import { useSelector } from 'react-redux'

interface IActionBarProps {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  nbSelectedOffers: number
  refreshOffers: () => void
  selectedOfferIds: string[]
  toggleSelectAllCheckboxes: () => void
  audience: Audience
}

const getUpdateActiveStatusAdapter = (
  areAllOffersSelected: boolean,
  searchFilters: Partial<TSearchFilters>,
  isActive: boolean,
  nbSelectedOffers: number,
  selectedOfferIds: string[],
  audience: Audience
) => {
  if (areAllOffersSelected) {
    if (audience === Audience.COLLECTIVE) {
      return () =>
        updateAllCollectiveOffersActiveStatusAdapter({
          searchFilters: { ...searchFilters, isActive },
          nbSelectedOffers,
        })
    }

    return () =>
      updateAllOffersActiveStatusAdapter({
        searchFilters: { ...searchFilters, isActive },
        nbSelectedOffers,
      })
  }

  if (audience === Audience.COLLECTIVE) {
    return () =>
      updateCollectiveOffersActiveStatusAdapter({
        ids: selectedOfferIds,
        isActive,
      })
  }

  return () =>
    updateOffersActiveStatusAdapter({ ids: selectedOfferIds, isActive })
}

const ActionsBar = ({
  refreshOffers,
  selectedOfferIds,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  nbSelectedOffers,
  audience,
}: IActionBarProps): JSX.Element => {
  const logEvent = useSelector((state: RootState) => state.app.logEvent)
  const searchFilters = useSelector(searchFiltersSelector)
  const notify = useNotification()
  const location = useLocation()

  const handleClose = useCallback(() => {
    clearSelectedOfferIds()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }, [clearSelectedOfferIds, areAllOffersSelected, toggleSelectAllCheckboxes])

  const handleUpdateOffersStatus = useCallback(
    async (isActivating: boolean) => {
      const adapter = getUpdateActiveStatusAdapter(
        areAllOffersSelected,
        searchFilters,
        isActivating,
        nbSelectedOffers,
        selectedOfferIds,
        audience
      )

      const { isOk, message } = await adapter()
      refreshOffers()

      if (!isOk) {
        notify.error(message)
      }

      areAllOffersSelected ? notify.pending(message) : notify.success(message)
      handleClose()
    },
    [
      searchFilters,
      selectedOfferIds,
      areAllOffersSelected,
      refreshOffers,
      nbSelectedOffers,
      handleClose,
      notify,
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
      {isConfirmDialogOpen && (
        <ConfirmDialog
          cancelText={'Annuler'}
          confirmText={'Désactiver'}
          onCancel={() => {
            logEvent(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
              from: location.pathname,
              has_selected_all_offers: areAllOffersSelected,
            })
            setIsConfirmDialogOpen(false)
          }}
          onConfirm={() => {
            logEvent(Events.CLICKED_DISABLED_SELECTED_OFFERS, {
              from: location.pathname,
              has_selected_all_offers: areAllOffersSelected,
            })
            handleDeactivate()
          }}
          icon={EyeIcon}
          title={
            nbSelectedOffers === 1
              ? `Vous avez sélectionné ${nbSelectedOffers} offre,`
              : `Vous avez sélectionné ${nbSelectedOffers} offres,`
          }
          secondTitle={
            nbSelectedOffers === 1
              ? `êtes-vous sûr de vouloir la désactiver${NBSP}?`
              : `êtes-vous sûr de vouloir toutes les désactiver${NBSP}?`
          }
        >
          {nbSelectedOffers === 1
            ? 'Dans ce cas, elle ne sera plus visible sur l’application pass Culture.'
            : 'Dans ce cas, elles ne seront plus visibles sur l’application pass Culture.'}
        </ConfirmDialog>
      )}
      <div className="actions-container">
        <button
          className="primary-button with-icon"
          onClick={() => setIsConfirmDialogOpen(true)}
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
          Publier
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
