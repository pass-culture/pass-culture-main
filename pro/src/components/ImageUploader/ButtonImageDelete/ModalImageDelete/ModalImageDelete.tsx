import React from 'react'

import ConfirmDialog from 'components/ConfirmDialog'
import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'

export interface IModalImageDeleteProps {
  isLoading: boolean
  onConfirm: () => void
  onDismiss: () => void
}

const ModalImageDelete = ({
  isLoading,
  onConfirm,
  onDismiss,
}: IModalImageDeleteProps): JSX.Element => {
  return (
    <ConfirmDialog
      cancelText="Retour"
      confirmText="Supprimer"
      icon={TrashIcon}
      isLoading={isLoading}
      onCancel={onDismiss}
      onConfirm={onConfirm}
      title="Supprimer l'image"
    >
      Souhaitez-vous vraiment supprimer cette image ?
    </ConfirmDialog>
  )
}

export default ModalImageDelete
