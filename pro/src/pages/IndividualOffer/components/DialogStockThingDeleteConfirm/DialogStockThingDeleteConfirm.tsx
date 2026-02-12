import strokeTrashIcon from '@/icons/stroke-trash.svg'
import { ConfirmDialog } from '@/ui-kit/ConfirmDialog/ConfirmDialog'

interface DialogStockDeleteConfirmProps {
  onConfirm: () => void
  onCancel: () => void
  isDialogOpen: boolean
}

export const DialogStockThingDeleteConfirm = ({
  onConfirm,
  onCancel,
  isDialogOpen,
}: DialogStockDeleteConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Voulez-vous supprimer ce stock ?"
      confirmText="Supprimer"
      cancelText="Annuler"
      icon={strokeTrashIcon}
      open={isDialogOpen}
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
