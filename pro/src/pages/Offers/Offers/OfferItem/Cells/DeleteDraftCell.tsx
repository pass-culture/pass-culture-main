import React, { useCallback, useState } from 'react'
import { useSWRConfig } from 'swr'

import { ListOffersOfferResponseModel } from 'apiClient/v1'
import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { DEFAULT_SEARCH_FILTERS } from 'core/Offers/constants'
import { useQuerySearchFilters } from 'core/Offers/hooks/useQuerySearchFilters'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import { GET_OFFERS_QUERY_KEY } from 'pages/Offers/OffersRoute'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

import { deleteDraftOffersAdapter } from '../../adapters/deleteDraftOffers'
import styles from '../OfferItem.module.scss'

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
    const { isOk, message } = await deleteDraftOffersAdapter({
      ids: [offer.id.toString()],
    })

    if (!isOk) {
      notification.error(message)
    } else {
      notification.success(message)
      logEvent?.(Events.DELETE_DRAFT_OFFER, {
        from: OFFER_FORM_NAVIGATION_IN.OFFERS,
        used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_TRASH_ICON,
        offerId: offer.id,
        isDraft: true,
      })
      await mutate([GET_OFFERS_QUERY_KEY, apiFilters])
    }

    setIsConfirmDialogOpen(false)
  }

  return (
    <>
      {isConfirmDialogOpen && (
        <ConfirmDialog
          icon={strokeTrashIcon}
          cancelText="Annuler"
          confirmText="Supprimer ce brouillon"
          onCancel={closeDeleteDraftDialog}
          onConfirm={onConfirmDeleteDraftOffer}
          title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
        />
      )}
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
