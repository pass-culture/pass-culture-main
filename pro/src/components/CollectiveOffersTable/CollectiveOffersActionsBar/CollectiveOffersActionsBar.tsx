import { useRef, useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateAllowedAction,
} from 'apiClient/v1'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import { useQueryCollectiveSearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { getCollectiveOffersSwrKeys } from 'commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { computeActivationSuccessMessage } from 'components/OffersTable/utils/computeActivationSuccessMessage'
import { computeSelectedOffersLabel } from 'components/OffersTable/utils/computeSelectedOffersLabel'
import fullHideIcon from 'icons/full-hide.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeThingIcon from 'icons/stroke-thing.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { CollectiveDeactivationConfirmDialog } from './CollectiveDeactivationConfirmDialog'

export type CollectiveOffersActionsBarProps = {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  selectedOffers: CollectiveOfferResponseModel[]
  areTemplateOffers: boolean
  searchButtonRef?: React.RefObject<HTMLButtonElement>
}

const computeDeactivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? 'offres ont bien été mises en pause'
      : 'offre a bien été mise en pause'
  return `${nbSelectedOffers} ${successMessage}`
}

const toggleCollectiveOffersActiveInactiveStatus = async (
  newStatus:
    | CollectiveOfferDisplayedStatus.PUBLISHED
    | CollectiveOfferDisplayedStatus.HIDDEN,
  selectedOffers: CollectiveOfferResponseModel[],
  notify: ReturnType<typeof useNotification>
) => {
  //  Differenciate template and bookable selected offers so that there can be two separarate api status update calls
  const collectiveOfferIds = []
  const collectiveOfferTemplateIds = []

  if (
    selectedOffers.some(
      (offer) =>
        offer.displayedStatus === CollectiveOfferDisplayedStatus.ARCHIVED
    )
  ) {
    notify.error(
      `Une erreur est survenue lors de ${newStatus === CollectiveOfferDisplayedStatus.PUBLISHED ? 'la publication' : 'la désactivation'} des offres sélectionnées`
    )
    return
  }

  for (const offer of selectedOffers) {
    if (offer.isShowcase) {
      collectiveOfferTemplateIds.push(offer.id)
    } else {
      collectiveOfferIds.push(offer.id)
    }
  }

  if (collectiveOfferIds.length > 0) {
    await api.patchCollectiveOffersActiveStatus({
      ids: collectiveOfferIds.map((id) => Number(id)),
      isActive: newStatus === CollectiveOfferDisplayedStatus.PUBLISHED,
    })
  }

  if (collectiveOfferTemplateIds.length > 0) {
    await api.patchCollectiveOffersTemplateActiveStatus({
      ids: collectiveOfferTemplateIds.map((ids) => Number(ids)),
      isActive: newStatus === CollectiveOfferDisplayedStatus.PUBLISHED,
    })
  }
}

export function CollectiveOffersActionsBar({
  selectedOffers,
  clearSelectedOfferIds,
  areAllOffersSelected,
  areTemplateOffers,
  searchButtonRef,
}: CollectiveOffersActionsBarProps) {
  const urlSearchFilters = useQueryCollectiveSearchFilters()

  const notify = useNotification()
  const [isDeactivationDialogOpen, setIsDeactivationDialogOpen] =
    useState(false)
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false)

  const selectedOffererId = useSelector(selectCurrentOffererId)?.toString()

  const isNewOffersAndBookingsActive = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_OFFERS_AND_BOOKINGS_STRUCTURE'
  )

  const archiveButtonRef = useRef<HTMLButtonElement>(null)
  const deActivateButtonRef = useRef<HTMLButtonElement>(null)

  const { mutate } = useSWRConfig()

  const collectiveOffersQueryKeys = getCollectiveOffersSwrKeys({
    isNewOffersAndBookingsActive,
    isInTemplateOffersPage: areTemplateOffers,
    urlSearchFilters,
    selectedOffererId,
  })

  async function updateOfferStatus(
    newSatus:
      | CollectiveOfferDisplayedStatus.ARCHIVED
      | CollectiveOfferDisplayedStatus.HIDDEN
      | CollectiveOfferDisplayedStatus.PUBLISHED
  ) {
    switch (newSatus) {
      case CollectiveOfferDisplayedStatus.PUBLISHED: {
        const updateOfferStatusMessage = getPublishOffersErrorMessage()
        if (!updateOfferStatusMessage) {
          try {
            await toggleCollectiveOffersActiveInactiveStatus(
              CollectiveOfferDisplayedStatus.PUBLISHED,
              selectedOffers,
              notify
            )
            await mutate(collectiveOffersQueryKeys)
            notify.success(
              computeActivationSuccessMessage(selectedOffers.length)
            )
          } catch {
            notify.error('Une erreur est survenue')
          }
        } else {
          notify.error(updateOfferStatusMessage)
          return
        }
        break
      }
      case CollectiveOfferDisplayedStatus.HIDDEN: {
        try {
          await toggleCollectiveOffersActiveInactiveStatus(
            CollectiveOfferDisplayedStatus.HIDDEN,
            selectedOffers,
            notify
          )
          await mutate(collectiveOffersQueryKeys)
          notify.success(
            computeDeactivationSuccessMessage(selectedOffers.length)
          )
        } catch {
          notify.error('Une erreur est survenue')
        }
        setIsDeactivationDialogOpen(false)
        break
      }
      case CollectiveOfferDisplayedStatus.ARCHIVED: {
        try {
          await onArchiveOffers()
          await mutate(collectiveOffersQueryKeys)
          notify.success(
            selectedOffers.length > 1
              ? `${selectedOffers.length} offres ont bien été archivées`
              : 'Une offre a bien été archivée',
            {
              duration: NOTIFICATION_LONG_SHOW_DURATION,
            }
          )
        } catch {
          notify.error(
            'Une erreur est survenue lors de l’archivage de l’offre',
            {
              duration: NOTIFICATION_LONG_SHOW_DURATION,
            }
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
        offer.isShowcase
          ? CollectiveOfferTemplateAllowedAction.CAN_ARCHIVE
          : CollectiveOfferAllowedAction.CAN_ARCHIVE
      )
    })
    if (archivableOffers.length < selectedOffers.length) {
      notify.error(
        'Les offres déjà archivées ou liées à des réservations ne peuvent pas être archivées'
      )
      clearSelectedOfferIds()
    } else {
      setIsArchiveDialogOpen(true)
    }
  }

  function openHideOffersDialog() {
    selectedOffers.map((offer) => {
      if (
        !isActionAllowedOnCollectiveOffer(
          offer,
          CollectiveOfferTemplateAllowedAction.CAN_HIDE
        )
      ) {
        notify.error(
          `Seules les offres vitrines au statut publié peuvent être mises en pause.`
        )
        clearSelectedOfferIds()
        return
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
      notify.error(
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

    notify.success(
      computeActivationSuccessMessage(offersWithCanPublishAction.length)
    )

    clearSelectedOfferIds()
  }

  const onArchiveOffers = async () => {
    const collectiveOfferIds = []
    const collectiveOfferTemplateIds = []

    for (const offer of selectedOffers) {
      if (offer.isShowcase) {
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

  function getPublishOffersErrorMessage() {
    if (
      selectedOffers.some(
        (offer) =>
          offer.displayedStatus === CollectiveOfferDisplayedStatus.ARCHIVED
      )
    ) {
      notify.error(
        `Une erreur est survenue lors de la publication des offres sélectionnées`
      )
      return
    }
    if (
      selectedOffers.some(
        (offer) =>
          offer.displayedStatus === CollectiveOfferDisplayedStatus.DRAFT
      )
    ) {
      return 'Vous ne pouvez pas publier des brouillons depuis cette liste'
    }
    if (selectedOffers.some((offer) => offer.hasBookingLimitDatetimesPassed)) {
      return 'Vous ne pouvez pas publier des offres collectives dont la date de réservation est passée'
    }
    return ''
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
          >
            Annuler
          </Button>
          <Button
            onClick={openArchiveOffersDialog}
            icon={strokeThingIcon}
            variant={ButtonVariant.SECONDARY}
            ref={archiveButtonRef}
          >
            Archiver
          </Button>
          <Button
            onClick={openHideOffersDialog}
            icon={fullHideIcon}
            variant={ButtonVariant.SECONDARY}
            ref={deActivateButtonRef}
          >
            Mettre en pause
          </Button>
          <Button
            onClick={publishOffers}
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
