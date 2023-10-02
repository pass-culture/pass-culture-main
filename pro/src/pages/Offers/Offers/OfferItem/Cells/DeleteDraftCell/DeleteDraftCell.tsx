import React, { useCallback, useState } from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullTrashIcon from 'icons/full-trash.svg'
import strokeTrashIcon from 'icons/stroke-trash.svg'
import ListIconButton from 'ui-kit/ListIconButton/ListIconButton'

import { deleteDraftOffersAdapter } from '../../../adapters/deleteDraftOffers'
import styles from '../../OfferItem.module.scss'

interface DeleteDraftOffersProps {
  offer: Offer
  refreshOffers: () => void
}

const DeleteDraftCell = ({ offer, refreshOffers }: DeleteDraftOffersProps) => {
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const notification = useNotification()
  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogOpen(false)
  }, [])

  const onConfirmDeleteDraftOffer = useCallback(async () => {
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
      refreshOffers()
    }

    setIsConfirmDialogOpen(false)
  }, [offer])

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

export default DeleteDraftCell
