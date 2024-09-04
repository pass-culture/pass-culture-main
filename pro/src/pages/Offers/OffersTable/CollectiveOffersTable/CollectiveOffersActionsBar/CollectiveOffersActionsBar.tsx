import { useState } from 'react'
import { mutate } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { ArchiveConfirmationModal } from 'components/ArchiveConfirmationModal/ArchiveConfirmationModal'
import { canArchiveCollectiveOffer } from 'components/ArchiveConfirmationModal/utils/canArchiveCollectiveOffer'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from 'config/swrQueryKeys'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQueryCollectiveSearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { CollectiveSearchFiltersParams } from 'core/Offers/types'
import { useNotification } from 'hooks/useNotification'
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
  toggleSelectAllCheckboxes: () => void
  getUpdateOffersStatusMessage: (selectedOfferIds: number[]) => string
}

const computeDeactivationSuccessMessage = (nbSelectedOffers: number) => {
  const successMessage =
    nbSelectedOffers > 1
      ? `offres ont bien été masquées`
      : `offre a bien été masquée`
  return `${nbSelectedOffers} ${successMessage}`
}

const updateCollectiveOffersStatus = async (
  isActive: boolean,
  selectedOffers: CollectiveOfferResponseModel[],
  notify: ReturnType<typeof useNotification>,
  apiFilters: CollectiveSearchFiltersParams
) => {
  try {
    //  Differenciate template and bookable selected offers so that there can be two separarate api status update calls
    const collectiveOfferIds = []
    const collectiveOfferTemplateIds = []

    if (!canPublishCollectiveOffersArchived(selectedOffers)) {
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres sélectionnées`
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
        isActive,
      })
    }

    if (collectiveOfferTemplateIds.length > 0) {
      await api.patchCollectiveOffersTemplateActiveStatus({
        ids: collectiveOfferTemplateIds.map((ids) => Number(ids)),
        isActive,
      })
    }

    notify.information(
      isActive
        ? computeActivationSuccessMessage(selectedOffers.length)
        : computeDeactivationSuccessMessage(selectedOffers.length)
    )
  } catch {
    notify.error('Une erreur est survenue')
  }

  await mutate([GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters])
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

function canPublishCollectiveOffersArchived(
  offers: CollectiveOfferResponseModel[]
) {
  return offers.every((offer) => {
    //  Check that all the offers are published or expired
    return offer.status !== CollectiveOfferStatus.ARCHIVED
  })
}

export function CollectiveOffersActionsBar({
  selectedOffers,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  getUpdateOffersStatusMessage,
}: CollectiveOffersActionsBarProps) {
  const urlSearchFilters = useQueryCollectiveSearchFilters()

  const notify = useNotification()
  const [isDeactivationDialogOpen, setIsDeactivationDialogOpen] =
    useState(false)
  const [isArchiveDialogOpen, setIsArchiveDialogOpen] = useState(false)

  const apiFilters = {
    ...DEFAULT_COLLECTIVE_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const handleClose = () => {
    clearSelectedOfferIds()
    areAllOffersSelected && toggleSelectAllCheckboxes()
  }

  function onDeactivateOffersClicked() {
    if (!canDeactivateCollectiveOffers(selectedOffers)) {
      notify.error(
        'Seules les offres au statut publié ou expiré peuvent être masquées.'
      )
      return
    }
    setIsDeactivationDialogOpen(true)
  }

  const handleUpdateOffersStatus = async (isActivating: boolean) => {
    await updateCollectiveOffersStatus(
      isActivating,
      selectedOffers,
      notify,
      apiFilters
    )

    handleClose()
  }

  const handleActivate = async () => {
    const updateOfferStatusMessage = getUpdateOffersStatusMessage(
      selectedOffers.map((offer) => offer.id)
    )
    if (!updateOfferStatusMessage) {
      await handleUpdateOffersStatus(true)
    } else {
      notify.error(updateOfferStatusMessage)
    }
  }

  const handleDeactivateOffers = async () => {
    await handleUpdateOffersStatus(false)
    setIsDeactivationDialogOpen(false)
  }

  const onArchiveOffersClicked = () => {
    const shouldOpenArchiveDialog = selectedOffers.every((offer) => {
      if (!canArchiveCollectiveOffer(offer)) {
        notify.error(
          'Les offres liées à des réservations en cours ne peuvent pas être archivées'
        )
        return false
      }
      return true
    })
    setIsArchiveDialogOpen(shouldOpenArchiveDialog)
  }

  const archiveOffer = async () => {
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

      if (collectiveOfferTemplateIds.length > 0) {
        await api.patchCollectiveOffersTemplateArchive({
          ids: [...collectiveOfferTemplateIds],
        })
      }

      if (collectiveOfferIds.length > 0) {
        await api.patchCollectiveOffersArchive({ ids: [...collectiveOfferIds] })
      }

      await mutate([GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters])

      notify.success(
        selectedOffers.length > 1
          ? `${selectedOffers.length} offres ont bien été archivée`
          : 'Une offre a bien été archivée',
        {
          duration: NOTIFICATION_LONG_SHOW_DURATION,
        }
      )
      setIsArchiveDialogOpen(false)
    } catch (error) {
      notify.error('Une erreur est survenue lors de l’archivage de l’offre', {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }

  return (
    <>
      {isDeactivationDialogOpen && (
        <CollectiveDeactivationConfirmDialog
          areAllOffersSelected={areAllOffersSelected}
          nbSelectedOffers={selectedOffers.length}
          onConfirm={handleDeactivateOffers}
          onCancel={() => setIsDeactivationDialogOpen(false)}
        />
      )}

      {isArchiveDialogOpen && (
        <ArchiveConfirmationModal
          onDismiss={() => setIsArchiveDialogOpen(false)}
          onValidate={archiveOffer}
          hasMultipleOffers={selectedOffers.length > 1}
        />
      )}

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          {computeSelectedOffersLabel(selectedOffers.length)}
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
          <Button onClick={handleClose} variant={ButtonVariant.SECONDARY}>
            Annuler
          </Button>
          <Button
            onClick={onArchiveOffersClicked}
            icon={strokeThingIcon}
            variant={ButtonVariant.SECONDARY}
          >
            Archiver
          </Button>
          <Button
            onClick={onDeactivateOffersClicked}
            icon={fullHideIcon}
            variant={ButtonVariant.SECONDARY}
          >
            Masquer
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
