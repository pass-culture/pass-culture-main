import { ConfirmDialog } from 'components/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

import styles from './DialogStockDeleteConfirm.module.scss'

interface DialogStockDeleteConfirmProps {
  onConfirm: () => void
  onCancel: () => void
  isDialogOpen: boolean
}

export const DialogStockEventDeleteConfirm = ({
  onConfirm,
  onCancel,
  isDialogOpen,
}: DialogStockDeleteConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Voulez-vous supprimer cette date ?"
      confirmText="Confirmer la suppression"
      cancelText="Annuler"
      icon={strokeTrashIcon}
      open={isDialogOpen}
    >
      <p className={styles['first-block']}>
        {'Elle ne sera plus disponible à la réservation et '}
        <strong>
          entraînera l’annulation des réservations en cours et validées !
        </strong>
      </p>
      <p>
        L’ensemble des utilisateurs concernés sera automatiquement averti par
        email.
      </p>
    </ConfirmDialog>
  )
}
