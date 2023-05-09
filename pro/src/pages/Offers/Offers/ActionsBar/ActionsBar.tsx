import React, { useCallback } from 'react'
import { useSelector } from 'react-redux'

import ActionsBarSticky from 'components/ActionsBarSticky'
import { TSearchFilters } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import { searchFiltersSelector } from 'store/offers/selectors'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { deleteDraftOffersAdapter } from '../adapters/deleteDraftOffers'

import { updateAllCollectiveOffersActiveStatusAdapter } from './adapters/updateAllCollectiveOffersActiveStatusAdapter'
import { updateAllOffersActiveStatusAdapter } from './adapters/updateAllOffersActiveStatusAdapter'
import { updateCollectiveOffersActiveStatusAdapter } from './adapters/updateCollectiveOffersActiveStatusAdapter'
import { updateOffersActiveStatusAdapter } from './adapters/updateOffersActiveStatusAdapter'
import DeactivationConfirmDialog from './ConfirmDialog/DeactivationConfirmDialog'
import DeleteConfirmDialog from './ConfirmDialog/DeleteConfirmDialog'

export interface IActionBarProps {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  nbSelectedOffers: number
  refreshOffers: () => void
  tmpSelectedOfferIds: string[]
  toggleSelectAllCheckboxes: () => void
  audience: Audience
  getUpdateOffersStatusMessage: (selectedOfferIds: string[]) => string
  canDeleteOffers: (selectedOfferIds: string[]) => boolean
}

const getUpdateActiveStatusAdapter = (
  areAllOffersSelected: boolean,
  searchFilters: Partial<TSearchFilters>,
  isActive: boolean,
  nbSelectedOffers: number,
  tmpSelectedOfferIds: string[],
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
        ids: tmpSelectedOfferIds,
        isActive,
      })
  }

  return () =>
    updateOffersActiveStatusAdapter({ ids: tmpSelectedOfferIds, isActive })
}

const ActionsBar = ({
  refreshOffers,
  tmpSelectedOfferIds,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  nbSelectedOffers,
  audience,
  getUpdateOffersStatusMessage,
  canDeleteOffers,
}: IActionBarProps): JSX.Element => {
  const searchFilters = useSelector(searchFiltersSelector)
  const notify = useNotification()
  const {
    visible: isConfirmDialogOpen,
    showModal: showConfirmDialog,
    hideModal: hideConfirmDialog,
  } = useModal()
  const {
    visible: isDeleteDialogOpen,
    showModal: showDeleteDialog,
    hideModal: hideDeleteDialog,
  } = useModal()

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
        tmpSelectedOfferIds,
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
      areAllOffersSelected,
      refreshOffers,
      nbSelectedOffers,
      tmpSelectedOfferIds,
      handleClose,
      notify,
    ]
  )

  const handleActivate = useCallback(() => {
    const updateOfferStatusMessage =
      getUpdateOffersStatusMessage(tmpSelectedOfferIds)
    if (!updateOfferStatusMessage) {
      handleUpdateOffersStatus(true)
    } else {
      notify.error(updateOfferStatusMessage)
    }
  }, [handleUpdateOffersStatus])

  const handleDeactivate = useCallback(() => {
    handleUpdateOffersStatus(false)
    hideConfirmDialog()
  }, [handleUpdateOffersStatus])

  const computeSelectedOffersLabel = () => {
    if (nbSelectedOffers > 1) {
      return `${getOffersCountToDisplay(nbSelectedOffers)} offres sélectionnées`
    }

    return `${nbSelectedOffers} offre sélectionnée`
  }

  const handleDelete = useCallback(async () => {
    if (!canDeleteOffers(tmpSelectedOfferIds)) {
      notify.error('Seuls les  brouillons peuvent être supprimés')
      return
    }
    const { isOk, message } = await deleteDraftOffersAdapter({
      ids: tmpSelectedOfferIds,
      nbSelectedOffers,
    })
    if (!isOk) {
      notify.error(message)
    } else {
      notify.success(message)
      refreshOffers()
      clearSelectedOfferIds()
    }
    hideDeleteDialog()
  }, [tmpSelectedOfferIds, nbSelectedOffers])

  const handleOpenDeleteDialog = () => {
    if (!canDeleteOffers(tmpSelectedOfferIds)) {
      notify.error('Seuls les brouillons peuvent être supprimés')
      return
    }
    showDeleteDialog()
  }

  const Left = () => <span>{computeSelectedOffersLabel()}</span>

  const Right = () => (
    <>
      <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
        Annuler
      </Button>
      <Button onClick={() => showConfirmDialog()} Icon={StatusInactiveIcon}>
        Désactiver
      </Button>
      {audience == Audience.INDIVIDUAL && (
        <Button onClick={() => handleOpenDeleteDialog()} Icon={TrashFilledIcon}>
          Supprimer
        </Button>
      )}
      <Button onClick={handleActivate} Icon={StatusValidatedIcon}>
        Publier
      </Button>
    </>
  )

  return (
    <>
      {isConfirmDialogOpen && (
        <DeactivationConfirmDialog
          areAllOffersSelected={areAllOffersSelected}
          nbSelectedOffers={nbSelectedOffers}
          onConfirm={handleDeactivate}
          onCancel={hideConfirmDialog}
          audience={audience}
        />
      )}
      {isDeleteDialogOpen && (
        <DeleteConfirmDialog
          onCancel={hideDeleteDialog}
          nbSelectedOffers={nbSelectedOffers}
          handleDelete={handleDelete}
        />
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
