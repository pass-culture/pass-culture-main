import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import Trash from 'icons/ico-trash.svg'

interface IDialogStockDeleteConfirmProps {
  onConfirm: () => void
  onCancel: () => void
}

const DialogStockThingDeleteConfirm = ({
  onConfirm,
  onCancel,
}: IDialogStockDeleteConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Voulez-vous supprimer ce stock ?"
      confirmText="Supprimer"
      cancelText="Annuler"
      icon={Trash}
    >
      <p>
        {'Ce stock ne sera plus disponible à la réservation et '}
        <strong>entraînera l’annulation des réservations en cours !</strong>
      </p>
      <p>
        L’ensemble des utilisateurs concernés sera automatiquement averti par
        e-mail.
      </p>
    </ConfirmDialog>
  )
}

export default DialogStockThingDeleteConfirm
