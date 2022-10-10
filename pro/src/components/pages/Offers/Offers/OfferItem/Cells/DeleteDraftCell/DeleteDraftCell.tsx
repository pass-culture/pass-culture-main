import React, { useCallback, useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import { Offer } from 'core/Offers/types'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import ConfirmDialog from 'new_components/ConfirmDialog'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import TooltipWrapper from 'ui-kit/TooltipWrapper'

import { deleteDraftOffersAdapter } from '../../../adapters/deleteDraftOffers'
import styles from '../../OfferItem.module.scss'

const DeleteDraftCell = ({ offer }: { offer: Offer }) => {
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
    } else notification.success(message)

    setIsConfirmDialogOpen(false)
  }, [offer])

  return (
    <>
      {isConfirmDialogOpen && (
        <ConfirmDialog
          icon={TrashIcon}
          cancelText="Annuler"
          confirmText="Supprimer ce brouillon"
          onCancel={closeDeleteDraftDialog}
          onConfirm={onConfirmDeleteDraftOffer}
          title={`Voulez-vous supprimer le brouillon : "${offer.name}"`}
        >
          <></>
        </ConfirmDialog>
      )}
      <td className={styles['draft-column']} align="right">
        <TooltipWrapper title="Supprimer le brouillon" delay={0}>
          <Button
            variant={ButtonVariant.SECONDARY}
            onClick={() => setIsConfirmDialogOpen(true)}
            className={styles['button']}
          >
            <TrashFilledIcon
              title={`${offer.name} - supprimer le brouillon`}
              className={styles['button-icon']}
            />
          </Button>
        </TooltipWrapper>
      </td>
    </>
  )
}

export default DeleteDraftCell
