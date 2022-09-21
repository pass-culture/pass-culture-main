import React from 'react'

import { ReactComponent as Trash } from 'icons/ico-trash.svg'
import ConfirmDialog from 'new_components/ConfirmDialog'

interface IOfferEducationalModalProps {
  onDismiss(): void
  onValidate(): void
}

const CancelCollectiveBookingModal = ({
  onDismiss,
  onValidate,
}: IOfferEducationalModalProps): JSX.Element => {
  return (
    <ConfirmDialog
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

export default CancelCollectiveBookingModal
