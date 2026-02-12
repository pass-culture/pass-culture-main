import type React from 'react'

import strokeTrashIcon from '@/icons/stroke-trash.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface ModalImageDeleteProps {
  isLoading: boolean
  onConfirm: () => void
  onDismiss: () => void
  isDialogOpen: boolean
  trigger: React.ReactNode
}

export const ModalImageDelete = ({
  isLoading,
  onConfirm,
  onDismiss,
  isDialogOpen,
  trigger,
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
      trigger={trigger}
    >
      Souhaitez-vous vraiment supprimer cette image ?
    </ConfirmDialog>
  )
}
