import React from 'react'

import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import ConfirmDialog from 'new_components/ConfirmDialog'

interface IDeleteConfirmDialogProps {
  setIsDeleteDialogOpen: (status: boolean) => void
  nbSelectedOffers: number
  handleDelete: () => void
}

const DeleteConfirmDialog = ({
  setIsDeleteDialogOpen,
  nbSelectedOffers,
  handleDelete,
}: IDeleteConfirmDialogProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText={'Annuler'}
      confirmText={'Supprimer ces brouillons'}
      onCancel={() => {
        setIsDeleteDialogOpen(false)
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
