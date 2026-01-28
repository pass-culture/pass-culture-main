import { useRef, useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
  type CollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { MAX_OFFERS_TO_DISPLAY } from '@/commons/core/Offers/constants'
import { useQueryCollectiveSearchFilters } from '@/commons/core/Offers/hooks/useQuerySearchFilters'
import { getCollectiveOffersSwrKeys } from '@/commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { ensureCurrentOfferer } from '@/commons/store/offerer/selectors'
import { isActionAllowedOnCollectiveOffer } from '@/commons/utils/isActionAllowedOnCollectiveOffer'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { ActionsBarSticky } from '@/components/ActionsBarSticky/ActionsBarSticky'
import { ArchiveConfirmationModal } from '@/components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullHideIcon from '@/icons/full-hide.svg'
import fullValidateIcon from '@/icons/full-validate.svg'
import strokeThingIcon from '@/icons/stroke-thing.svg'

import { CollectiveDeactivationConfirmDialog } from './CollectiveDeactivationConfirmDialog'

export type CollectiveOffersActionsBarProps<T> = {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  selectedOffers: T[]
  areTemplateOffers: boolean
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

const computeDeactivationSuccessMessage = (nbSelectedOffers: number) =>
  `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre a bien été mise', 'offres ont bien été mises')} en pause`

const computeActivationSuccessMessage = (nbSelectedOffers: number) =>
  `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre a bien été publiée', 'offres ont bien été publiées')}`

const computeSelectedOffersLabel = (nbSelectedOffers: number) =>
  nbSelectedOffers > MAX_OFFERS_TO_DISPLAY
    ? `${MAX_OFFERS_TO_DISPLAY}+ offres sélectionnées`
    : `${nbSelectedOffers} ${pluralizeFr(nbSelectedOffers, 'offre sélectionnée', 'offres sélectionnées')}`

const toggleCollectiveOffersActiveInactiveStatus = async <
  T extends {
    id: string | number
    displayedStatus: CollectiveOfferDisplayedStatus
  },
>(
  newStatus:
    | CollectiveOfferDisplayedStatus.PUBLISHED
    | CollectiveOfferDisplayedStatus.HIDDEN,
  selectedOffers: T[],
  areTemplateOffers: boolean = false,
  snackBar: ReturnType<typeof useSnackBar>
) => {
  //  Differenciate template and bookable selected offers so that there can be two separarate api status update calls

  if (
    selectedOffers.some(
      (offer) =>
        offer.displayedStatus === CollectiveOfferDisplayedStatus.ARCHIVED ||
        !areTemplateOffers
    )
  ) {
    const msg = `Une erreur est survenue lors de ${newStatus === CollectiveOfferDisplayedStatus.PUBLISHED ? 'la publication' : 'la désactivation'} des offres sélectionnées`
    snackBar.error(msg)
    throw new Error(msg)
  }

  const collectiveOfferTemplateIds = selectedOffers.map((offer) => offer.id)

  if (collectiveOfferTemplateIds.length > 0) {
    await api.patchCollectiveOffersTemplateActiveStatus({
      ids: collectiveOfferTemplateIds.map((ids) => Number(ids)),
      isActive: newStatus === CollectiveOfferDisplayedStatus.PUBLISHED,
    })
  }
}

export function CollectiveOffersActionsBar<
  T extends CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel,
>({
  selectedOffers,
  clearSelectedOfferIds,
  areAllOffersSelected,
  areTemplateOffers,
  searchButtonRef,
}: CollectiveOffersActionsBarProps<T>) {
  const urlSearchFilters = useQueryCollectiveSearchFilters()

  const snackBar = useSnackBar()
  const [isDeactivationDialogOpen, setIsDeactivationDialogOpen] =
    useState(false)
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false)

  const selectedOffererId = useAppSelector(ensureCurrentOfferer).id
  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const deActivateButtonRef = useRef<HTMLButtonElement>(null)

  const { mutate } = useSWRConfig()

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isInTemplateOffersPage: areTemplateOffers,
    urlSearchFilters,
    selectedOffererId,
  })

  async function updateOfferStatus(
    newSatus:
      | CollectiveOfferDisplayedStatus.ARCHIVED
      | CollectiveOfferDisplayedStatus.HIDDEN
  ) {
    switch (newSatus) {
      case CollectiveOfferDisplayedStatus.HIDDEN: {
        try {
          await toggleCollectiveOffersActiveInactiveStatus(
            CollectiveOfferDisplayedStatus.HIDDEN,
            selectedOffers,
            areTemplateOffers,
            snackBar
          )
          await mutate(collectiveOffersQueryKeys)
          snackBar.success(
            computeDeactivationSuccessMessage(selectedOffers.length)
          )
        } catch {
          snackBar.error('Une erreur est survenue')
        }
        setIsDeactivationDialogOpen(false)
        break
      }
      case CollectiveOfferDisplayedStatus.ARCHIVED: {
        try {
          await onArchiveOffers()
          await mutate(collectiveOffersQueryKeys)
          snackBar.success(
            selectedOffers.length > 1
              ? `${selectedOffers.length} offres ont bien été archivées`
              : 'Une offre a bien été archivée'
          )
        } catch {
          snackBar.error(
            'Une erreur est survenue lors de l’archivage de l’offre'
          )
        }
        setIsArchiveDialogOpen(false)
        break
      }
    }

    clearSelectedOfferIds()
  }

  function openArchiveOffersDialog() {
    const archivableOffers = selectedOffers.filter((offer) => {
      return isActionAllowedOnCollectiveOffer(
        offer,
        areTemplateOffers
          ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
          : CollectiveOfferAllowedAction.CAN_ARCHIVE
      )
    })
    if (archivableOffers.length < selectedOffers.length) {
      snackBar.error(
        'Les offres déjà archivées ou liées à des réservations ne peuvent pas être archivées'
      )
      clearSelectedOfferIds()
    } else {
      setIsArchiveDialogOpen(true)
    }
  }

  function openHideOffersDialog() {
    selectedOffers.forEach((offer) => {
      if (
        !isActionAllowedOnCollectiveOffer(
          offer,
          CollectiveOfferTemplateAllowedAction.CAN_HIDE
        )
      ) {
        snackBar.error(
          `Seules les offres vitrines au statut publié peuvent être mises en pause.`
        )
        clearSelectedOfferIds()
      }
    })

    setIsDeactivationDialogOpen(true)
  }

  async function publishOffers() {
    const offersWithCanPublishAction = selectedOffers.filter((offer) =>
      isActionAllowedOnCollectiveOffer(
        offer,
        CollectiveOfferTemplateAllowedAction.CAN_PUBLISH
      )
    )

    if (offersWithCanPublishAction.length < 1) {
      snackBar.error(
        `Seules les offres vitrines au statut en pause peuvent être publiées.`
      )
      clearSelectedOfferIds()
      return
    }

    if (offersWithCanPublishAction.length > 0) {
      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: offersWithCanPublishAction.map((offer) => Number(offer.id)),
        isActive: true,
      })
    }

    await mutate(collectiveOffersQueryKeys)

    snackBar.success(
      computeActivationSuccessMessage(offersWithCanPublishAction.length)
    )

    clearSelectedOfferIds()
  }

  const onArchiveOffers = async () => {
    const collectiveOfferIds = []
    const collectiveOfferTemplateIds = []

    for (const offer of selectedOffers) {
      if (areTemplateOffers) {
        collectiveOfferTemplateIds.push(offer.id)
      } else {
        collectiveOfferIds.push(offer.id)
      }
    }

    if (collectiveOfferTemplateIds.length > 0) {
      await api.patchCollectiveOffersTemplateArchive({
        ids: [...collectiveOfferTemplateIds],
      })
    }

    if (collectiveOfferIds.length > 0) {
      await api.patchCollectiveOffersArchive({ ids: [...collectiveOfferIds] })
    }
  }

  const getTemplateOffersCTAs = () => {
    const templateCTAs = (
      <>
        <Button
          onClick={openHideOffersDialog}
          icon={fullHideIcon}
          variant={ButtonVariant.SECONDARY}
          ref={deActivateButtonRef}
          label="Mettre en pause"
        />
        <Button
          onClick={publishOffers}
          icon={fullValidateIcon}
          variant={ButtonVariant.SECONDARY}
          label="Publier"
        />
      </>
    )
    if (areTemplateOffers) {
      return templateCTAs
    }
    return null
  }

  return (
    <>
      <CollectiveDeactivationConfirmDialog
        areAllOffersSelected={areAllOffersSelected}
        nbSelectedOffers={selectedOffers.length}
        onConfirm={async () => {
          await updateOfferStatus(CollectiveOfferDisplayedStatus.HIDDEN)
          setTimeout(() => {
            searchButtonRef?.current?.focus()
          })
        }}
        onCancel={() => setIsDeactivationDialogOpen(false)}
        isDialogOpen={isDeactivationDialogOpen}
        refToFocusOnClose={deActivateButtonRef}
      />

      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveDialogOpen(false)}
        onValidate={async () => {
          await updateOfferStatus(CollectiveOfferDisplayedStatus.ARCHIVED)
          setTimeout(() => {
            searchButtonRef?.current?.focus()
          })
        }}
        hasMultipleOffers={selectedOffers.length > 1}
        selectedOffers={selectedOffers}
        isDialogOpen={isArchiveDialogOpen}
        refToFocusOnClose={archiveButtonRef}
      />

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          {computeSelectedOffersLabel(selectedOffers.length)}
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button
            onClick={clearSelectedOfferIds}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Annuler"
          />
          <Button
            onClick={openArchiveOffersDialog}
            icon={strokeThingIcon}
            variant={ButtonVariant.SECONDARY}
            ref={archiveButtonRef}
            label="Archiver"
          />
          {getTemplateOffersCTAs()}
        </ActionsBarSticky.Right>
      </ActionsBarSticky>
    </>
  )
}
