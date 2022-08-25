import React from 'react'

import ConfirmDialog from 'new_components/ConfirmDialog'

import { ReactComponent as Trash } from './assets/trash.svg'
import styles from './OfferEducationalActionsModal.module.scss'

interface IOfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
}

const OfferEducationalModal = ({
  onDismiss,
  onValidate,
}: IOfferEducationalModalProps): JSX.Element => {
  return (
    <ConfirmDialog
      extraClassNames={styles['modal-icon-wrapper']}
      onCancel={onDismiss}
      onConfirm={onValidate}
      cancelText="Retour"
      confirmText="Confirmer"
      icon={Trash}
      title="Voulez-vous annuler la réservation ?"
    >
      <p>
        L’établissement scolaire concerné recevra un message lui indiquant
        l’annulation de sa réservation.
      </p>
    </ConfirmDialog>
  )
}

export default OfferEducationalModal
