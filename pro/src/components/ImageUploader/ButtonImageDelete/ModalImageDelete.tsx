import React from 'react'

import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

interface ModalImageDeleteProps {
  isLoading: boolean
  onConfirm: () => void
  onDismiss: () => void
  isDialogOpen: boolean
}

export const ModalImageDelete = ({
  isLoading,
  onConfirm,
  onDismiss,
  isDialogOpen,
}: ModalImageDeleteProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Retour"
      confirmText="Supprimer"
      icon={strokeTrashIcon}
      isLoading={isLoading}
      onCancel={onDismiss}
      onConfirm={onConfirm}
      title="Supprimer l’image"
      open={isDialogOpen}
    >
      Souhaitez-vous vraiment supprimer cette image ?
    </ConfirmDialog>
  )
}
