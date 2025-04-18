import { useState } from 'react'
import { useSelector } from 'react-redux'
import { mutate, useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  OfferStatus,
  type PatchAllOffersActiveStatusBodyModel,
} from 'apiClient/v1'
import { GET_OFFERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'commons/core/Offers/types'
import { serializeApiFilters } from 'commons/core/Offers/utils/serializer'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'
import { computeActivationSuccessMessage } from 'components/OffersTable/utils/computeActivationSuccessMessage'
import { computeSelectedOffersLabel } from 'components/OffersTable/utils/computeSelectedOffersLabel'
import fullHideIcon from 'icons/full-hide.svg'
import fullTrashIcon from 'icons/full-trash.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { computeDeletionErrorMessage } from 'pages/IndividualOffers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from 'pages/IndividualOffers/utils/computeDeletionSuccessMessage'
import { computeIndividualApiFilters } from 'pages/IndividualOffers/utils/computeIndividualApiFilters'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { DeleteConfirmDialog } from './components/DeleteConfirmDialog'
import { IndividualDeactivationConfirmDialog } from './components/IndividualDeactivationConfirmDialog'

export type IndividualOffersActionsBarProps = {
  areAllOffersSelected: boolean
  clearSelectedOffers: () => void
  selectedOffers: { id: number; status: OfferStatus }[]
  toggleSelectAllCheckboxes: () => void
  canDelete: boolean
  canPublish: boolean
  canDeactivate: boolean
}

const computeAllActivationSuccessMessage = (nbSelectedOffers: number) => {
  const activationWording =
    'en cours d’activation, veuillez rafraichir dans quelques instants'
  return nbSelectedOffers > 1
    ? `Les offres sont ${activationWording}`
    : `Une offre est ${activationWording}`
}

const computeAllDeactivationSuccessMessage = (nbSelectedOffers: number) =>
  nbSelectedOffers > 1
    ? 'Les offres sont en cours de désactivation, veuillez rafraichir dans quelques instants'
    : 'Une offre est en cours de désactivation, veuillez rafraichir dans quelques instants'

const computeDeactivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été mises en pause'
      : 'offre a bien été mise en pause'
  return `${nbSelectedOffers} ${successMessage}`
}

const updateIndividualOffersStatus = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  selectedOfferIds: number[],
  notify: ReturnType<typeof useNotification>,
  apiFilters: SearchFiltersParams
) => {
  const filters = serializeApiFilters(apiFilters)
  const payload: PatchAllOffersActiveStatusBodyModel = {
    categoryId: filters.categoryId ?? null,
    creationMode: filters.creationMode ?? null,
    isActive: isActive,
    nameOrIsbn: filters.nameOrIsbn ?? null,
    offererId: filters.offererId ?? null,
    periodBeginningDate: filters.periodBeginningDate ?? null,
    periodEndingDate: filters.periodEndingDate ?? null,
    status: filters.status ?? null,
    venueId: filters.venueId ?? null,
    offererAddressId: filters.offererAddressId ?? null,
  }
  const deactivationWording = 'la mise en pause'
  if (areAllOffersSelected) {
    //  Bulk edit if all editable offers are selected
    try {
      await api.patchAllOffersActiveStatus({
        ...payload,
        isActive,
      })
      notify.information(
        isActive
          ? computeAllActivationSuccessMessage(selectedOfferIds.length)
          : computeAllDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : deactivationWording
        } des offres`
      )
    }
  } else {
    try {
      await api.patchOffersActiveStatus({
        ids: selectedOfferIds.map((id) => Number(id)),
        isActive,
      })
      notify.success(
        isActive
          ? computeActivationSuccessMessage(selectedOfferIds.length)
          : computeDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : deactivationWording
        } des offres`
      )
    }
  }
  await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
}

export const IndividualOffersActionsBar = ({
  selectedOffers,
  clearSelectedOffers,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  canDelete,
  canPublish,
  canDeactivate,
}: IndividualOffersActionsBarProps): JSX.Element => {
  const isToggleAndMemorizeFiltersEnabled = useActiveFeature(
    'WIP_COLLAPSED_MEMORIZED_FILTERS'
  )
  const urlSearchFilters = useQuerySearchFilters()
  const { storedFilters } = getStoredFilterConfig('individual')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<SearchFiltersParams>)
      : {}),
  }

  const { mutate } = useSWRConfig()
  const selectedOffererId = useSelector(selectCurrentOffererId)?.toString()

  const notify = useNotification()
  const [isDeactivationDialogOpen, setIsDeactivationDialogOpen] =
    useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId
  )

  const handleClose = () => {
    clearSelectedOffers()
    if (areAllOffersSelected) {
      toggleSelectAllCheckboxes()
    }
  }

  const handleUpdateOffersStatus = async (isActivating: boolean) => {
    await updateIndividualOffersStatus(
      isActivating,
      areAllOffersSelected,
      selectedOffers
        .filter((offer) =>
          isActivating
            ? offer.status === OfferStatus.INACTIVE
            : offer.status === OfferStatus.ACTIVE ||
              offer.status === OfferStatus.SOLD_OUT ||
              offer.status === OfferStatus.EXPIRED
        )
        .map((offer) => offer.id),
      notify,
      apiFilters
    )

    handleClose()
  }

  const handleActivate = async () => {
    await handleUpdateOffersStatus(true)
  }

  const handleDeactivateOffers = async () => {
    await handleUpdateOffersStatus(false)
    setIsDeactivationDialogOpen(false)
  }

  const handleDelete = async () => {
    try {
      await api.deleteDraftOffers({
        ids: selectedOffers.map((offer) => offer.id),
      })
      notify.success(
        computeDeletionSuccessMessage(
          selectedOffers.filter((o) => o.status === OfferStatus.DRAFT).length
        )
      )
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
      clearSelectedOffers()
    } catch {
      notify.error(computeDeletionErrorMessage(selectedOffers.length))
    }
    setIsDeleteDialogOpen(false)
  }

  const handleOpenDeleteDialog = () => {
    setIsDeleteDialogOpen(true)
  }

  return (
    <>
      <IndividualDeactivationConfirmDialog
        areAllOffersSelected={areAllOffersSelected}
        nbSelectedOffers={
          selectedOffers.filter(
            (offer) =>
              offer.status === OfferStatus.ACTIVE ||
              offer.status === OfferStatus.SOLD_OUT ||
              offer.status === OfferStatus.EXPIRED
          ).length
        }
        onConfirm={handleDeactivateOffers}
        onCancel={() => setIsDeactivationDialogOpen(false)}
        isDialogOpen={isDeactivationDialogOpen}
      />

      <DeleteConfirmDialog
        nbSelectedOffers={
          selectedOffers.filter((offer) => offer.status === OfferStatus.DRAFT)
            .length
        }
        onConfirm={handleDelete}
        onCancel={() => setIsDeleteDialogOpen(false)}
        isDialogOpen={isDeleteDialogOpen}
      />

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          {computeSelectedOffersLabel(selectedOffers.length)}
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
            Annuler
          </Button>
          {canDeactivate && (
            <Button
              onClick={() => setIsDeactivationDialogOpen(true)}
              icon={fullHideIcon}
              variant={ButtonVariant.SECONDARY}
            >
              Mettre en pause
            </Button>
          )}
          {canDelete && (
            <Button
              onClick={handleOpenDeleteDialog}
              icon={fullTrashIcon}
              variant={ButtonVariant.SECONDARY}
            >
              Supprimer
            </Button>
          )}
          {canPublish && (
            <Button
              onClick={handleActivate}
              icon={fullValidateIcon}
              variant={ButtonVariant.SECONDARY}
            >
              Publier
            </Button>
          )}
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
