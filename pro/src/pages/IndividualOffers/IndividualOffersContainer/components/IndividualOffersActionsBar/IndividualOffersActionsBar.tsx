import { useRef, useState } from 'react'
import { mutate, useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import {
  OfferStatus,
  type PatchAllOffersActiveStatusBodyModel,
} from '@/apiClient/v1'
import { GET_OFFERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { MAX_OFFERS_TO_DISPLAY } from '@/commons/core/Offers/constants'
import { useQuerySearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import type { IndividualSearchFiltersParams } from '@/commons/core/Offers/types'
import { serializeApiIndividualFilters } from '@/commons/core/Offers/utils/serializeApiIndividualFilters'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { getStoredFilterConfig } from '@/components/OffersTableSearch/utils'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullHideIcon from '@/icons/full-hide.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import { computeDeletionErrorMessage } from '@/pages/IndividualOffers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from '@/pages/IndividualOffers/utils/computeDeletionSuccessMessage'
import { computeIndividualApiFilters } from '@/pages/IndividualOffers/utils/computeIndividualApiFilters'

import { DeleteConfirmDialog } from './components/DeleteConfirmDialog'
import { IndividualDeactivationConfirmDialog } from './components/IndividualDeactivationConfirmDialog'

export type IndividualOffersActionsBarProps = {
  areAllOffersSelected: boolean
  clearSelectedOffers: () => void
  selectedOffers: { id: number; status: OfferStatus }[]
  canDelete: boolean
  canPublish: boolean
  canDeactivate: boolean
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

const computeAllActivationSuccessMessage = (nbSelectedOffers: number) =>
  `${pluralizeFr(nbSelectedOffers, 'Une offre est', 'Les offres sont')} en cours d’activation, veuillez rafraichir dans quelques instants.`

const computeAllDeactivationSuccessMessage = (nbSelectedOffers: number) =>
  `${pluralizeFr(nbSelectedOffers, 'Une offre est', 'Les offres sont')} en cours de désactivation, veuillez rafraichir dans quelques instants.`

const computeDeactivationSuccessMessage = (nbSelectedOffers: number) =>
  `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre a bien été mise', 'offres ont bien été mises')} en pause`

const computeActivationSuccessMessage = (nbSelectedOffers: number) =>
  `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre a bien été publiée ', 'offres ont bien été publiées')}`

const computeSelectedOffersLabel = (nbSelectedOffers: number) =>
  nbSelectedOffers > MAX_OFFERS_TO_DISPLAY
    ? `${MAX_OFFERS_TO_DISPLAY}+ offres sélectionnées`
    : `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre sélectionnée', 'offres sélectionnées')}`

const updateIndividualOffersStatus = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  selectedOfferIds: number[],
  snackBar: ReturnType<typeof useSnackBar>,
  apiFilters: IndividualSearchFiltersParams
) => {
  const filters = serializeApiIndividualFilters(apiFilters)
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
      snackBar.success(
        isActive
          ? computeAllActivationSuccessMessage(selectedOfferIds.length)
          : computeAllDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch {
      snackBar.error(
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
      snackBar.success(
        isActive
          ? computeActivationSuccessMessage(selectedOfferIds.length)
          : computeDeactivationSuccessMessage(selectedOfferIds.length)
      )
    } catch {
      snackBar.error(
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
  areAllOffersSelected,
  canDelete,
  canPublish,
  canDeactivate,
  searchButtonRef,
}: IndividualOffersActionsBarProps): JSX.Element => {
  const urlSearchFilters = useQuerySearchFilters()
  const { storedFilters } = getStoredFilterConfig('individual')
  const finalSearchFilters = {
    ...urlSearchFilters,
    ...(storedFilters as Partial<IndividualSearchFiltersParams>),
  }

  const { mutate } = useSWRConfig()
  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id

  const deleteButtonRef = useRef<HTMLButtonElement>(null)
  const dactivateButtonRef = useRef<HTMLButtonElement>(null)

  const snackBar = useSnackBar()
  const [isDeactivationDialogOpen, setIsDeactivationDialogOpen] =
    useState(false)
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false)

  const apiFilters = computeIndividualApiFilters(
    finalSearchFilters,
    selectedOffererId
  )

  const handleClose = () => {
    clearSelectedOffers()
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
      snackBar,
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

    setTimeout(() => {
      searchButtonRef?.current?.focus()
    })
  }

  const handleDelete = async () => {
    try {
      await api.deleteDraftOffers({
        ids: selectedOffers.map((offer) => offer.id),
      })
      snackBar.success(
        computeDeletionSuccessMessage(
          selectedOffers.filter((o) => o.status === OfferStatus.DRAFT).length
        )
      )
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
      clearSelectedOffers()
    } catch {
      snackBar.error(computeDeletionErrorMessage(selectedOffers.length))
    }
    setIsDeleteDialogOpen(false)

    setTimeout(() => {
      searchButtonRef?.current?.focus()
    })
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
        refToFocusOnClose={dactivateButtonRef}
      />

      <DeleteConfirmDialog
        nbSelectedOffers={
          selectedOffers.filter((offer) => offer.status === OfferStatus.DRAFT)
            .length
        }
        onConfirm={handleDelete}
        onCancel={() => setIsDeleteDialogOpen(false)}
        isDialogOpen={isDeleteDialogOpen}
        refToFocusOnClose={deleteButtonRef}
      />

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          {computeSelectedOffersLabel(selectedOffers.length)}
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button
            onClick={handleClose}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
          />

          {canDeactivate && (
            <Button
              onClick={() => setIsDeactivationDialogOpen(true)}
              icon={fullHideIcon}
              variant={ButtonVariant.SECONDARY}
              ref={dactivateButtonRef}
              label="Mettre en pause"
            />
          )}
          {canDelete && (
            <Button
              onClick={handleOpenDeleteDialog}
              icon={fullTrashIcon}
              variant={ButtonVariant.SECONDARY}
              ref={deleteButtonRef}
              label="Supprimer"
            />
          )}
          {canPublish && (
            <Button
              onClick={handleActivate}
              icon={fullValidateIcon}
              variant={ButtonVariant.SECONDARY}
              label="Publier"
            />
          )}
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
