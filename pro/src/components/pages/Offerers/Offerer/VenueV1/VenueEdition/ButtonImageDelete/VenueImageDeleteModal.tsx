import React from 'react'

import { ReactComponent as TrashIcon } from 'icons/ico-trash.svg'
import ConfirmDialog from 'new_components/ConfirmDialog'

interface IVenueImageDeleteModalProps {
  isLoading: boolean
  onDeleteImage: () => void
  onDismiss: () => void
}

export const VenueImageDeleteModal = ({
  isLoading,
  onDeleteImage,
  onDismiss,
}: IVenueImageDeleteModalProps): JSX.Element => (
  <ConfirmDialog
    cancelText="Retour"
    confirmText="Supprimer"
    icon={TrashIcon}
    isLoading={isLoading}
    onCancel={onDismiss}
    onConfirm={onDeleteImage}
    title="Supprimer l'image"
  >
    Souhaitez-vous vraiment supprimer cette image ?
  </ConfirmDialog>
)
