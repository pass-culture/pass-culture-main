import React, { useCallback, useState } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import useNotification from 'components/hooks/useNotification'
import { getOffersCountToDisplay } from 'components/pages/Offers/domain/getOffersCountToDisplay'
import { Events } from 'core/FirebaseEvents/constants'
import { TSearchFilters } from 'core/Offers/types'
import { Audience, NBSP } from 'core/shared'
import { ReactComponent as EyeIcon } from 'icons/ico-eye-hidden.svg'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import ActionsBarSticky from 'new_components/ActionsBarSticky'
import ConfirmDialog from 'new_components/ConfirmDialog'
import { searchFiltersSelector } from 'store/offers/selectors'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { updateAllCollectiveOffersActiveStatusAdapter } from './adapters/updateAllCollectiveOffersActiveStatusAdapter'
import { updateAllOffersActiveStatusAdapter } from './adapters/updateAllOffersActiveStatusAdapter'
import { updateCollectiveOffersActiveStatusAdapter } from './adapters/updateCollectiveOffersActiveStatusAdapter'
import { updateOffersActiveStatusAdapter } from './adapters/updateOffersActiveStatusAdapter'

export interface IActionBarProps {
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
  const { logEvent } = useAnalytics()
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

  const Left = () => <span>{computeSelectedOffersLabel()}</span>

  const Right = () => (
    <>
      <Button
        onClick={() => setIsConfirmDialogOpen(true)}
        Icon={StatusInactiveIcon}
      >
        Désactiver
      </Button>
      <Button onClick={handleActivate} Icon={StatusValidatedIcon}>
        Publier
      </Button>
      <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
        Annuler
      </Button>
    </>
  )

  return (
    <>
      {isConfirmDialogOpen && (
        <ConfirmDialog
          cancelText={'Annuler'}
          confirmText={'Désactiver'}
          onCancel={() => {
            logEvent?.(Events.CLICKED_CANCELED_SELECTED_OFFERS, {
              from: location.pathname,
              has_selected_all_offers: areAllOffersSelected,
            })
            setIsConfirmDialogOpen(false)
          }}
          onConfirm={() => {
            logEvent?.(Events.CLICKED_DISABLED_SELECTED_OFFERS, {
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
      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <Left />
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Right />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}

export default ActionsBar
