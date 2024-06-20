import { useState } from 'react'
import { mutate } from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  CollectiveOfferResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { ActionsBarSticky } from 'components/ActionsBarSticky/ActionsBarSticky'
import { GET_COLLECTIVE_OFFERS_QUERY_KEY } from 'config/swrQueryKeys'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import { SearchFiltersParams } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils/serializer'
import { Audience } from 'core/shared/types'
import { useNotification } from 'hooks/useNotification'
import fullHideIcon from 'icons/full-hide.svg'
import fullValidateIcon from 'icons/full-validate.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'

import { DeactivationConfirmDialog } from './DeactivationConfirmDialog/DeactivationConfirmDialog'
import {
  computeActivationSuccessMessage,
  computeAllActivationSuccessMessage,
  computeAllDeactivationSuccessMessage,
  computeDeactivationSuccessMessage,
  computeSelectedOffersLabel,
} from './utils'

export type CollectiveOffersActionsBarProps = {
  areAllOffersSelected: boolean
  clearSelectedOfferIds: () => void
  selectedOfferIds: number[]
  selectedOffers: CollectiveOfferResponseModel[]
  toggleSelectAllCheckboxes: () => void
  getUpdateOffersStatusMessage: (selectedOfferIds: number[]) => string
}

const handleCollectiveOffers = async (
  isActive: boolean,
  areAllOffersSelected: boolean,
  selectedOffers: CollectiveOfferResponseModel[],
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
      notify.error(
        `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres sélectionnées`
      )
    }
  }

  await mutate([GET_COLLECTIVE_OFFERS_QUERY_KEY, apiFilters])
}

function canDeactivateCollectiveOffers(offers: CollectiveOfferResponseModel[]) {
  return offers.every((offer) => {
    //  Check that all the offers are published or expired
    return (
      offer.status === OfferStatus.ACTIVE ||
      (offer.status === OfferStatus.EXPIRED &&
        (!offer.booking?.booking_status ||
          offer.booking.booking_status === CollectiveBookingStatus.CANCELLED))
    )
  })
}

export function CollectiveOffersActionsBar({
  selectedOfferIds,
  selectedOffers,
  clearSelectedOfferIds,
  toggleSelectAllCheckboxes,
  areAllOffersSelected,
  getUpdateOffersStatusMessage,
}: CollectiveOffersActionsBarProps) {
  const urlSearchFilters = useQuerySearchFilters()

  const notify = useNotification()
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)

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
    if (!canDeactivateCollectiveOffers(selectedOffers)) {
      notify.error(
        'Seules les offres au statut publié ou expiré peuvent être désactivées.'
      )
      return
    }
    setIsConfirmDialogOpen(true)
  }

  const handleUpdateOffersStatus = async (isActivating: boolean) => {
    await handleCollectiveOffers(
      isActivating,
      areAllOffersSelected,
      selectedOffers,
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

  return (
    <>
      {isConfirmDialogOpen && (
        <DeactivationConfirmDialog
          areAllOffersSelected={areAllOffersSelected}
          nbSelectedOffers={selectedOfferIds.length}
          onConfirm={handleDeactivateOffers}
          onCancel={() => setIsConfirmDialogOpen(false)}
          audience={Audience.COLLECTIVE}
        />
      )}

      <ActionsBarSticky>
        <ActionsBarSticky.Left>
          <span role="status">
            {computeSelectedOffersLabel(selectedOfferIds.length)}
          </span>
        </ActionsBarSticky.Left>
        <ActionsBarSticky.Right>
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
