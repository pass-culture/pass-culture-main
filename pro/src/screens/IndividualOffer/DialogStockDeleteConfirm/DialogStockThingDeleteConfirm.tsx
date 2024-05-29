import React from 'react'

import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

interface DialogStockDeleteConfirmProps {
  onConfirm: () => void
  onCancel: () => void
}

export const DialogStockThingDeleteConfirm = ({
  onConfirm,
  onCancel,
}: DialogStockDeleteConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Voulez-vous supprimer ce stock ?"
      confirmText="Supprimer"
      cancelText="Annuler"
      icon={strokeTrashIcon}
    >
      <p>
        {'Ce stock ne sera plus disponible à la réservation et '}
        <strong>entraînera l’annulation des réservations en cours !</strong>
      </p>
      <p>
        L’ensemble des utilisateurs concernés sera automatiquement averti par
        email.
      </p>
    </ConfirmDialog>
  )
}
