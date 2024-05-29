import { useState } from 'react'
import { mutate, useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from 'config/swrQueryKeys'
import { isOfferEducational } from 'core/OfferEducational/types'
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
  selectedOfferIds: number[]
  selectedOffers: (
    | CollectiveOfferResponseModel
    | ListOffersOfferResponseModel
  )[]
  toggleSelectAllCheckboxes: () => void
  audience: Audience
  getUpdateOffersStatusMessage: (selectedOfferIds: number[]) => string
  canDeleteOffers: () => boolean
}

const handleCollectiveOffers = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  selectedOffers: (
    | CollectiveOfferResponseModel
    | ListOffersOfferResponseModel
  )[],
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
          ? computeAllActivationSuccessMessage(selectedOffers.length)
          : computeAllDeactivationSuccessMessage(selectedOffers.length)
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

      for (const offer of selectedOffers) {
        if (offer.isShowcase) {
          collectiveOfferTemplateIds.push(offer.id)
        } else {
          collectiveOfferIds.push(offer.id)
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
          ? computeActivationSuccessMessage(selectedOffers.length)
          : computeDeactivationSuccessMessage(selectedOffers.length)
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

function canDeactivateCollectiveOffers(
  offers: (CollectiveOfferResponseModel | ListOffersOfferResponseModel)[]
) {
  return offers.every((offer) => {
    if (!isOfferEducational(offer)) {
      return false
    }

    //  Check that all the offers are published or expired
    return (
      offer.status === OfferStatus.ACTIVE ||
      (offer.status === OfferStatus.EXPIRED &&
        (!offer.booking?.booking_status ||
          offer.booking.booking_status === CollectiveBookingStatus.CANCELLED))
    )
  })
}

export const ActionsBar = ({
  selectedOfferIds,
  selectedOffers,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
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

  function onDeactivateOffersClicked() {
    if (
      audience === Audience.COLLECTIVE &&
      !canDeactivateCollectiveOffers(selectedOffers)
    ) {
      notify.error(
        'Seules les offres au statut publié ou expiré peuvent être désactivées.'
      )
      return
    }
    setIsConfirmDialogOpen(true)
  }

  const handleUpdateOffersStatus = async (isActivating: boolean) => {
    if (audience === Audience.COLLECTIVE) {
      await handleCollectiveOffers(
        isActivating,
        areAllOffersSelected,
        selectedOffers,
        notify,
        apiFilters
      )
    } else {
      await handleIndividualOffers(
        isActivating,
        areAllOffersSelected,
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
    if (!canDeleteOffers()) {
      notify.error('Seuls les  brouillons peuvent être supprimés')
      return
    }
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

  const Left = () => <span role="status">{computeSelectedOffersLabel()}</span>

  const Right = () => (
    <>
      <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
        Annuler
      </Button>
      <Button
        onClick={onDeactivateOffersClicked}
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
          nbSelectedOffers={selectedOfferIds.length}
          onConfirm={handleDeactivateOffers}
          onCancel={() => setIsConfirmDialogOpen(false)}
          audience={audience}
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
          <Left />
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Right />
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
