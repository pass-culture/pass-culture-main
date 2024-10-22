import { useState } from 'react'
import { useSelector } from 'react-redux'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferDisplayedStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'commons/core/Notification/constants'
import { useQueryCollectiveSearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { getCollectiveOffersSwrKeys } from 'commons/core/Offers/utils/getCollectiveOffersSwrKeys'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { useNotification } from 'commons/hooks/useNotification'
import { selectCurrentOffererId } from 'commons/store/user/selectors'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { canArchiveCollectiveOffer } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import fullHideIcon from 'icons/full-hide.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import strokeThingIcon from 'icons/stroke-thing.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { computeActivationSuccessMessage } from '../../../utils/computeActivationSuccessMessage'
import { computeSelectedOffersLabel } from '../../../utils/computeSelectedOffersLabel'

import { CollectiveDeactivationConfirmDialog } from './CollectiveDeactivationConfirmDialog'

export type CollectiveOffersActionsBarProps = {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  selectedOffers: CollectiveOfferResponseModel[]
  areTemplateOffers: boolean
}

const computeDeactivationSuccessMessage = (
  nbSelectedOffers: number,
  areNewStatusesEnabled: boolean
) => {
  const deactivationWording = areNewStatusesEnabled
    ? 'mise en pause'
    : 'masquée'
  const successMessage =
    nbSelectedOffers > 1
      ? `offres ont bien été ${deactivationWording}s`
      : `offre a bien été ${deactivationWording}`
  return `${nbSelectedOffers} ${successMessage}`
}

function canDeactivateCollectiveOffers(offers: CollectiveOfferResponseModel[]) {
  return offers.every((offer) => {
    //  Check that all the offers are published or expired
    return (
      offer.status === CollectiveOfferStatus.ACTIVE ||
      (offer.status === CollectiveOfferStatus.EXPIRED &&
        (!offer.booking?.booking_status ||
          offer.booking.booking_status === CollectiveBookingStatus.CANCELLED))
    )
  })
}

const toggleCollectiveOffersActiveInactiveStatus = async (
  newStatus:
    | CollectiveOfferDisplayedStatus.ACTIVE
    | CollectiveOfferDisplayedStatus.INACTIVE,
  selectedOffers: CollectiveOfferResponseModel[],
  notify: ReturnType<typeof useNotification>
) => {
  //  Differenciate template and bookable selected offers so that there can be two separarate api status update calls
  const collectiveOfferIds = []
  const collectiveOfferTemplateIds = []

  if (
    selectedOffers.some(
      (offer) => offer.status === CollectiveOfferStatus.ARCHIVED
    )
  ) {
    notify.error(
      `Une erreur est survenue lors de ${newStatus === CollectiveOfferDisplayedStatus.ACTIVE ? 'la publication' : 'la désactivation'} des offres sélectionnées`
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
      isActive: newStatus === CollectiveOfferDisplayedStatus.ACTIVE,
    })
  }

  if (collectiveOfferTemplateIds.length > 0) {
    await api.patchCollectiveOffersTemplateActiveStatus({
      ids: collectiveOfferTemplateIds.map((ids) => Number(ids)),
      isActive: newStatus === CollectiveOfferDisplayedStatus.ACTIVE,
    })
  }
}

export function CollectiveOffersActionsBar({
  selectedOffers,
  clearSelectedOfferIds,
  areAllOffersSelected,
  areTemplateOffers,
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
  const areNewStatusesEnabled = useActiveFeature(
    'ENABLE_COLLECTIVE_NEW_STATUSES'
  )

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
      | CollectiveOfferDisplayedStatus.INACTIVE
      | CollectiveOfferDisplayedStatus.ACTIVE
  ) {
    switch (newSatus) {
      case CollectiveOfferDisplayedStatus.ACTIVE: {
        const updateOfferStatusMessage = getPublishOffersErrorMessage()
        if (!updateOfferStatusMessage) {
          try {
            await toggleCollectiveOffersActiveInactiveStatus(
              CollectiveOfferDisplayedStatus.ACTIVE,
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
      case CollectiveOfferDisplayedStatus.INACTIVE: {
        try {
          await toggleCollectiveOffersActiveInactiveStatus(
            CollectiveOfferDisplayedStatus.INACTIVE,
            selectedOffers,
            notify
          )
          await mutate(collectiveOffersQueryKeys)
          notify.success(
            computeDeactivationSuccessMessage(
              selectedOffers.length,
              areNewStatusesEnabled
            )
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
    const shouldOpenArchiveDialog = selectedOffers.every((offer) => {
      if (!canArchiveCollectiveOffer(offer)) {
        notify.error(
          'Les offres liées à des réservations en cours ne peuvent pas être archivées'
        )
        clearSelectedOfferIds()
        return false
      }
      return true
    })
    setIsArchiveDialogOpen(shouldOpenArchiveDialog)
  }

  function openDeactivateOffersDialog() {
    if (!canDeactivateCollectiveOffers(selectedOffers)) {
      notify.error(
        `Seules les offres au statut publié ou expiré peuvent être ${areNewStatusesEnabled ? 'mises en pause' : 'masquées'}.`
      )
      clearSelectedOfferIds()
      return
    }
    setIsDeactivationDialogOpen(true)
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
        (offer) => offer.status === CollectiveOfferStatus.ARCHIVED
      )
    ) {
      notify.error(
        `Une erreur est survenue lors de la publication des offres sélectionnées`
      )
      return
    }
    if (
      selectedOffers.some(
        (offer) => offer.status === CollectiveOfferStatus.DRAFT
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
        onConfirm={() =>
          updateOfferStatus(CollectiveOfferDisplayedStatus.INACTIVE)
        }
        onCancel={() => setIsDeactivationDialogOpen(false)}
        isDialogOpen={isDeactivationDialogOpen}
      />

      <ArchiveConfirmationModal
        onDismiss={() => setIsArchiveDialogOpen(false)}
        onValidate={() =>
          updateOfferStatus(CollectiveOfferDisplayedStatus.ARCHIVED)
        }
        hasMultipleOffers={selectedOffers.length > 1}
        selectedOffers={selectedOffers}
        isDialogOpen={isArchiveDialogOpen}
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
          >
            Archiver
          </Button>
          <Button
            onClick={openDeactivateOffersDialog}
            icon={fullHideIcon}
            variant={ButtonVariant.SECONDARY}
          >
            {areNewStatusesEnabled ? 'Mettre en pause' : 'Masquer'}
          </Button>
          <Button
            onClick={() =>
              updateOfferStatus(CollectiveOfferDisplayedStatus.ACTIVE)
            }
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
