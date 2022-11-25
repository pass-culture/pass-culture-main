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
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import { Button } from 'ui-kit'
import { IconPositionEnum, ButtonVariant } from 'ui-kit/Button/types'

import { deleteDraftOffersAdapter } from '../../../adapters/deleteDraftOffers'
import styles from '../../OfferItem.module.scss'

interface IDeleteDraftOffers {
  offer: Offer
  refreshOffers: () => void
}

const DeleteDraftCell = ({ offer, refreshOffers }: IDeleteDraftOffers) => {
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const { logEvent } = useAnalytics()
  const notification = useNotification()
  const closeDeleteDraftDialog = useCallback(() => {
    /* istanbul ignore next */
    setIsConfirmDialogOpen(false)
  }, [])

  const onConfirmDeleteDraftOffer = useCallback(async () => {
    const { isOk, message } = await deleteDraftOffersAdapter({
      ids: [offer.id],
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
      <td className={styles['draft-column']} align="right">
        {isConfirmDialogOpen && (
          <ConfirmDialog
            icon={TrashIcon}
            cancelText="Annuler"
            confirmText="Supprimer ce brouillon"
            onCancel={closeDeleteDraftDialog}
            onConfirm={onConfirmDeleteDraftOffer}
            title={`Voulez-vous supprimer le brouillon : "${offer.name}" ?`}
          />
        )}
        <Button
          variant={ButtonVariant.SECONDARY}
          onClick={() => setIsConfirmDialogOpen(true)}
          className={styles['button']}
          Icon={TrashFilledIcon}
          iconPosition={IconPositionEnum.CENTER}
          hasTooltip
        >
          Supprimer le brouillon
        </Button>
      </td>
    </>
  )
}

export default DeleteDraftCell
