import React, { useCallback, useState } from 'react'

import { Offer } from 'core/Offers/types'
import useNotification from 'hooks/useNotification'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import ConfirmDialog from 'new_components/ConfirmDialog'
import { Button } from 'ui-kit'
import { ButtonVariant, IconPositionEnum } from 'ui-kit/Button/types'

import { deleteDraftOffersAdapter } from '../../../adapters/deleteDraftOffers'
import styles from '../../OfferItem.module.scss'

interface IDeleteDraftOffers {
  offer: Offer
  refreshOffers: () => void
}

const DeleteDraftCell = ({ offer, refreshOffers }: IDeleteDraftOffers) => {
  const [isConfirmDialogOpen, setIsConfirmDialogOpen] = useState(false)
  const notification = useNotification()
  const closeDeleteDraftDialog = useCallback(() => {
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
