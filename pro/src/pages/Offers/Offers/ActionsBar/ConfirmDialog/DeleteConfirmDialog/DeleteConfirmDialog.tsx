import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'

interface DeleteConfirmDialogProps {
  onCancel: () => void
  nbSelectedOffers: number
  handleDelete: () => void
}

const DeleteConfirmDialog = ({
  onCancel,
  nbSelectedOffers,
  handleDelete,
}: DeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Supprimer ces brouillons'}
      onCancel={() => {
        onCancel()
      }}
      onConfirm={() => {
        handleDelete()
      }}
      icon={TrashIcon}
      title={
        nbSelectedOffers === 1
          ? `Voulez-vous supprimer ce brouillon ?`
          : `Voulez-vous supprimer ces ${nbSelectedOffers} brouillons ?`
      }
    >
      <></>
    </ConfirmDialog>
  )
}

export default DeleteConfirmDialog
