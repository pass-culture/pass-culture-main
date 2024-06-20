import { useState } from 'react'
import { mutate, useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import { useNotification } from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { getOffersCountToDisplay } from 'pages/Offers/domain/getOffersCountToDisplay'
import { GET_OFFERS_QUERY_KEY } from 'pages/Offers/OffersRoute'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import {
  computeDeletionErrorMessage,
  computeDeletionSuccessMessage,
} from '../utils'

import { DeactivationConfirmDialog } from './DeactivationConfirmDialog/DeactivationConfirmDialog'
import { DeleteConfirmDialog } from './DeleteConfirmDialog'
import {
  computeActivationSuccessMessage,
  computeAllActivationSuccessMessage,
  computeAllDeactivationSuccessMessage,
  computeDeactivationSuccessMessage,
} from './utils'

export interface IndividualOffersActionsBarProps {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  selectedOfferIds: number[]
  toggleSelectAllCheckboxes: () => void
  getUpdateOffersStatusMessage: (selectedOfferIds: number[]) => string
  canDeleteOffers: () => boolean
}

const handleIndividualOffers = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  selectedOfferIds: number[],
  notify: ReturnType<typeof useNotification>,
  apiFilters: SearchFiltersParams
) => {
  const payload = serializeApiFilters(apiFilters)
  if (areAllOffersSelected) {
    try {
      await api.patchAllOffersActiveStatus({
        ...payload,
        isActive,
      })
      notify.pending(
        isActive
          ? computeAllActivationSuccessMessage(selectedOfferIds.length)
          : computeAllDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch (error) {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres`
      )
    }
  } else {
    try {
      await api.patchOffersActiveStatus({
        ids: selectedOfferIds.map((id) => Number(id)),
        isActive,
      })
      notify.information(
        isActive
          ? computeActivationSuccessMessage(selectedOfferIds.length)
          : computeDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch (error) {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres`
      )
    }
  }

  await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
}

export const IndividualOffersActionsBar = ({
  selectedOfferIds,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  getUpdateOffersStatusMessage,
  canDeleteOffers,
}: IndividualOffersActionsBarProps): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const { mutate } = useSWRConfig()

  const notify = useNotification()
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const handleClose = () => {
    clearSelectedOfferIds()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }

  const handleUpdateOffersStatus = async (isActivating: boolean) => {
    await handleIndividualOffers(
      isActivating,
      areAllOffersSelected,
      selectedOfferIds,
      notify,
      apiFilters
    )

    handleClose()
  }

  const handleActivate = async () => {
    const updateOfferStatusMessage =
      getUpdateOffersStatusMessage(selectedOfferIds)
    if (!updateOfferStatusMessage) {
      await handleUpdateOffersStatus(true)
    } else {
      notify.error(updateOfferStatusMessage)
    }
  }

  const handleDeactivateOffers = async () => {
    await handleUpdateOffersStatus(false)
    setIsConfirmDialogOpen(false)
  }

  const computeSelectedOffersLabel = () => {
    if (selectedOfferIds.length > 1) {
      return `${getOffersCountToDisplay(selectedOfferIds.length)} offres sélectionnées`
    }

    return `${selectedOfferIds.length} offre sélectionnée`
  }

  const handleDelete = async () => {
    try {
      await api.deleteDraftOffers({
        ids: selectedOfferIds.map((id) => Number(id)),
      })
      notify.success(computeDeletionSuccessMessage(selectedOfferIds.length))
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
      clearSelectedOfferIds()
    } catch {
      notify.error(computeDeletionErrorMessage(selectedOfferIds.length))
    }
    setIsDeleteDialogOpen(false)
  }

  const handleOpenDeleteDialog = () => {
    if (!canDeleteOffers()) {
      notify.error('Seuls les brouillons peuvent être supprimés')
      return
    }
    setIsDeleteDialogOpen(true)
  }

  return (
    <>
      {isConfirmDialogOpen && (
        <DeactivationConfirmDialog
          areAllOffersSelected={areAllOffersSelected}
          nbSelectedOffers={selectedOfferIds.length}
          onConfirm={handleDeactivateOffers}
          onCancel={() => setIsConfirmDialogOpen(false)}
          audience={Audience.INDIVIDUAL}
        />
      )}

      {isDeleteDialogOpen && (
        <DeleteConfirmDialog
          onCancel={() => setIsDeleteDialogOpen(false)}
          nbSelectedOffers={selectedOfferIds.length}
          handleDelete={handleDelete}
        />
      )}

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <span role="status">{computeSelectedOffersLabel()}</span>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
            Annuler
          </Button>
          <Button
            onClick={() => setIsConfirmDialogOpen(true)}
            icon={fullHideIcon}
            variant={ButtonVariant.SECONDARY}
          >
            Désactiver
          </Button>
          <Button
            onClick={() => handleOpenDeleteDialog()}
            icon={fullTrashIcon}
            variant={ButtonVariant.SECONDARY}
          >
            Supprimer
          </Button>
          <Button
            onClick={handleActivate}
            icon={fullValidateIcon}
            variant={ButtonVariant.SECONDARY}
          >
            Publier
          </Button>
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
