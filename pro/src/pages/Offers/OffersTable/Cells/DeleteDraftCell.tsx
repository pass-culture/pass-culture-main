import { useCallback, useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'commons/core/FirebaseEvents/constants'
import { DEFAULT_SEARCH_FILTERS } from 'commons/core/Offers/constants'
import { useQuerySearchFilters } from 'commons/core/Offers/hooks/useQuerySearchFilters'
import { useNotification } from 'commons/hooks/useNotification'
import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { GET_OFFERS_QUERY_KEY } from 'pages/Offers/OffersRoute'
import { computeDeletionErrorMessage } from 'pages/Offers/utils/computeDeletionErrorMessage'
import { computeDeletionSuccessMessage } from 'pages/Offers/utils/computeDeletionSuccessMessage'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import styles from './Cells.module.scss'

interface DeleteDraftOffersProps {
  offer: ListOffersOfferResponseModel
}

export const DeleteDraftCell = ({ offer }: DeleteDraftOffersProps) => {
  const urlSearchFilters = useQuerySearchFilters()
  const { mutate } = useSWRConfig()
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const notification = useNotification()
  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogOpen(false)
  }, [])

  const apiFilters = {
    ...DEFAULT_SEARCH_FILTERS,
    ...urlSearchFilters,
  }
  delete apiFilters.page

  const onConfirmDeleteDraftOffer = async () => {
    try {
      await api.deleteDraftOffers({
        ids: [offer.id],
      })
      notification.success(computeDeletionSuccessMessage(1))
      logEvent(Events.DELETE_DRAFT_OFFER, {
        from: OFFER_FORM_NAVIGATION_IN.OFFERS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TRASH_ICON,
        offerId: offer.id,
        offerType: 'individual',
        isDraft: true,
      })
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
    } catch {
      notification.error(computeDeletionErrorMessage(1))
    }

    setIsConfirmDialogOpen(false)
  }

  return (
    <>
      <ConfirmDialog
        icon={strokeTrashIcon}
        cancelText="Annuler"
        confirmText="Supprimer ce brouillon"
        onCancel={closeDeleteDraftDialog}
        onConfirm={onConfirmDeleteDraftOffer}
        title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
        open={isConfirmDialogOpen}
      />
      <ListIconButton
        onClick={() => setIsConfirmDialogOpen(true)}
        className={styles['button']}
        icon={fullTrashIcon}
      >
        Supprimer
      </ListIconButton>
    </>
  )
}
