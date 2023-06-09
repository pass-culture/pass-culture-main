import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'
import { ReactComponent as Trash } from 'icons/ico-trash.svg'

import styles from './DialogStockDeleteConfirm.module.scss'

interface IDialogStockDeleteConfirmProps {
  onConfirm: () => void
  onCancel: () => void
}

const DialogStockEventDeleteConfirm = ({
  onConfirm,
  onCancel,
}: IDialogStockDeleteConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Voulez-vous supprimer cette occurrence ?"
      confirmText="Confirmer la suppression"
      cancelText="Annuler"
      icon={Trash}
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

export default DialogStockEventDeleteConfirm
