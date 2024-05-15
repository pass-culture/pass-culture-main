import { useState } from 'react'
import { mutate, useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from 'config/swrQueryKeys'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import useNotification from 'hooks/useNotification'
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

import { DeactivationConfirmDialog } from './ConfirmDialog/DeactivationConfirmDialog'
import { DeleteConfirmDialog } from './ConfirmDialog/DeleteConfirmDialog'
import {
  computeActivationSuccessMessage,
  computeAllActivationSuccessMessage,
  computeAllDeactivationSuccessMessage,
  computeDeactivationSuccessMessage,
} from './utils'

export interface ActionBarProps {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  nbSelectedOffers: number
  selectedOfferIds: string[]
  toggleSelectAllCheckboxes: () => void
  audience: Audience
  getUpdateOffersStatusMessage: (selectedOfferIds: string[]) => string
  canDeleteOffers: (selectedOfferIds: string[]) => boolean
}

const handleCollectiveOffers = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  nbSelectedOffers: number,
  selectedOfferIds: string[],
  notify: ReturnType<typeof useNotification>,
  apiFilters: SearchFiltersParams
) => {
  const payload = serializeApiFilters(apiFilters)
  if (areAllOffersSelected) {
    try {
      await api.patchAllCollectiveOffersActiveStatus({
        ...payload,
        isActive,
      })

      notify.pending(
        isActive
          ? computeAllActivationSuccessMessage(nbSelectedOffers)
          : computeAllDeactivationSuccessMessage(nbSelectedOffers)
      )
    } catch {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres`
      )
    }
  } else {
    try {
      const collectiveOfferIds = []
      const collectiveOfferTemplateIds = []

      for (const id of selectedOfferIds) {
        if (id.startsWith('T-')) {
          collectiveOfferTemplateIds.push(id.split('T-')[1])
        } else {
          collectiveOfferIds.push(id)
        }
      }

      await Promise.all([
        api.patchCollectiveOffersActiveStatus({
          ids: collectiveOfferIds.map((id) => Number(id)),
          isActive,
        }),
        api.patchCollectiveOffersTemplateActiveStatus({
          ids: collectiveOfferTemplateIds.map((ids) => Number(ids)),
          isActive,
        }),
      ])

      notify.information(
        isActive
          ? computeActivationSuccessMessage(nbSelectedOffers)
          : computeDeactivationSuccessMessage(nbSelectedOffers)
      )
    } catch {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres sélectionnées`
      )
    }
  }

  await mutate([GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters])
}

const handleIndividualOffers = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  nbSelectedOffers: number,
  selectedOfferIds: string[],
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
          ? computeAllActivationSuccessMessage(nbSelectedOffers)
          : computeAllDeactivationSuccessMessage(nbSelectedOffers)
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
          ? computeActivationSuccessMessage(nbSelectedOffers)
          : computeDeactivationSuccessMessage(nbSelectedOffers)
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

export const ActionsBar = ({
  selectedOfferIds,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  nbSelectedOffers,
  audience,
  getUpdateOffersStatusMessage,
  canDeleteOffers,
}: ActionBarProps): JSX.Element => {
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
    if (audience === Audience.COLLECTIVE) {
      await handleCollectiveOffers(
        isActivating,
        areAllOffersSelected,
        nbSelectedOffers,
        selectedOfferIds,
        notify,
        apiFilters
      )
    } else {
      await handleIndividualOffers(
        isActivating,
        areAllOffersSelected,
        nbSelectedOffers,
        selectedOfferIds,
        notify,
        apiFilters
      )
    }

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

  const handleDeactivate = async () => {
    await handleUpdateOffersStatus(false)
    setIsConfirmDialogOpen(false)
  }

  const computeSelectedOffersLabel = () => {
    if (nbSelectedOffers > 1) {
      return `${getOffersCountToDisplay(nbSelectedOffers)} offres sélectionnées`
    }

    return `${nbSelectedOffers} offre sélectionnée`
  }

  const handleDelete = async () => {
    if (!canDeleteOffers(selectedOfferIds)) {
      notify.error('Seuls les  brouillons peuvent être supprimés')
      return
    }
    try {
      await api.deleteDraftOffers({
        ids: selectedOfferIds.map((id) => Number(id)),
      })
      notify.success(computeDeletionSuccessMessage(nbSelectedOffers))
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
      clearSelectedOfferIds()
    } catch {
      notify.error(computeDeletionErrorMessage(nbSelectedOffers))
    }
    setIsDeleteDialogOpen(false)
  }

  const handleOpenDeleteDialog = () => {
    if (!canDeleteOffers(selectedOfferIds)) {
      notify.error('Seuls les brouillons peuvent être supprimés')
      return
    }
    setIsDeleteDialogOpen(true)
  }

  const Left = () => <span role="status">{computeSelectedOffersLabel()}</span>

  const Right = () => (
    <>
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
      {audience === Audience.INDIVIDUAL && (
        <Button
          onClick={() => handleOpenDeleteDialog()}
          icon={fullTrashIcon}
          variant={ButtonVariant.SECONDARY}
        >
          Supprimer
        </Button>
      )}
      <Button
        onClick={handleActivate}
        icon={fullValidateIcon}
        variant={ButtonVariant.SECONDARY}
      >
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
          onCancel={() => setIsConfirmDialogOpen(false)}
          audience={audience}
        />
      )}

      {isDeleteDialogOpen && (
        <DeleteConfirmDialog
          onCancel={() => setIsDeleteDialogOpen(false)}
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
